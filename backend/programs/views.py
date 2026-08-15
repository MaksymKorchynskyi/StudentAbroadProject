from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponsePermanentRedirect
from urllib.parse import urlencode
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from .models import Program
from .serializers import ProgramSerializer
from universities.models import University
import json
import logging
import re
import time
import requests as http_requests

logger = logging.getLogger(__name__)

# ... (API Views залишаються без змін) ...
class ProgramList(generics.ListCreateAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        queryset = Program.objects.filter(is_approved=True) if self.request.method == 'GET' else Program.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name_uk__icontains=search) | Q(name_en__icontains=search) |
                Q(description_uk__icontains=search) | Q(description_en__icontains=search) |
                Q(faculty_uk__icontains=search) | Q(faculty_en__icontains=search)
            )
        return queryset
    def perform_create(self, serializer):
        serializer.save(is_approved=False)

class ProgramDetail(generics.RetrieveAPIView):
    """Read-only API для перегляду окремої програми (Update/Delete — тільки через адмін-панель)"""
    queryset = Program.objects.filter(is_approved=True)
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

class UniversityPrograms(generics.ListAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        university_id = self.kwargs['university_id']
        return Program.objects.filter(university_id=university_id, is_approved=True)

class HomeUniversityPrograms(generics.ListAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        home_university = self.request.query_params.get('home_university', '')
        return Program.objects.filter(
            Q(home_university__name_uk__icontains=home_university) |
            Q(home_university__name_en__icontains=home_university),
            is_approved=True
        )

class ProgramOptions(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        options = {
            'study_levels': dict(Program.STUDY_LEVEL_CHOICES),
            'program_types': dict(Program.PROGRAM_TYPE_CHOICES)
        }
        return Response(options)

# --- VIEWS ДЛЯ САЙТУ ---

def program_list_page(request):
    programs = Program.objects.filter(is_approved=True).select_related(
        'university', 'home_university'
    ).order_by('-created_at')
    home_universities = University.objects.filter(home_programs__is_approved=True).distinct().order_by('name_uk')
    
    context = {
        'programs': programs,
        'home_universities': home_universities,
        # SEO Meta
        'meta_title': 'Study Abroad Programs | StudentAbroad',
        'meta_title_uk': 'Програми навчання за кордоном | StudentAbroad',
        'meta_description': 'Browse exchange programs for Ukrainian students. Find Bachelor, Master, and PhD opportunities at universities worldwide.',
        'meta_description_uk': 'Переглядай програми обміну для українських студентів. Знайди можливості бакалаврату, магістратури та PhD в університетах світу.',
    }
    return render(request, 'program-list.html', context)

def program_detail_page(request, slug=None):
    """
    View for program detail page.
    - Slug-based URLs (/program/<slug>/) render the page directly
    - Legacy URLs (?id=X) do 301 redirect to slug URL (preserving query params)
    """
    # Handle legacy ?id= parameter with 301 redirect
    if not slug:
        program_id = request.GET.get('id')
        if program_id:
            program = get_object_or_404(Program, pk=program_id)
            
            # Build redirect URL with preserved query params (except 'id')
            redirect_url = program.get_absolute_url()
            
            # Preserve other query params for marketing tracking
            query_params = request.GET.copy()
            query_params.pop('id', None)  # Remove 'id' param
            if query_params:
                redirect_url = f"{redirect_url}?{urlencode(query_params)}"
            
            return HttpResponsePermanentRedirect(redirect_url)
        else:
            # No slug and no id - return empty context
            return render(request, 'programs-read-more.html', {})
    
    # Slug-based URL - render the page
    program = get_object_or_404(
        Program.objects.select_related('university', 'home_university'),
        slug=slug,
        is_approved=True
    )
    
    # SEO Meta - dynamic from program data
    program_name = program.name_en or program.name_uk or 'Program'
    description = (program.description_en or program.description_uk or '')[:160]
    
    # Fallback if description is empty
    if not description:
        description = f"Learn about {program_name} exchange program at StudentAbroad. Find details about requirements, deadlines, and application process."
    
    context = {
        'program': program,
        'useful_links': program.get_useful_links_combined(),
        # SEO Meta
        'meta_title': f'{program_name} | StudentAbroad',
        'meta_description': description,
        'og_type': 'article',
        # Breadcrumbs for SEO
        'breadcrumbs': [
            {'name': 'Home', 'name_uk': 'Головна', 'url': '/'},
            {'name': 'Programs', 'name_uk': 'Програми', 'url': '/program-list.html'},
            {'name': program_name, 'name_uk': program.name_uk or program_name, 'url': program.get_absolute_url()},
        ],
    }
    return render(request, 'programs-read-more.html', context)


# ============================================================
# FORM PROTECTION HELPERS
# ============================================================

def _get_client_ip(request):
    """Отримує реальний IP клієнта (враховуючи Nginx/Cloudflare proxy)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _verify_turnstile(token, remote_ip):
    """Перевірка Cloudflare Turnstile токена на сервері."""
    if not settings.TURNSTILE_SECRET_KEY:
        # Turnstile не налаштований (локальна розробка) — пропускаємо
        return True
    
    if not token:
        return False
    
    try:
        response = http_requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={
                'secret': settings.TURNSTILE_SECRET_KEY,
                'response': token,
                'remoteip': remote_ip,
            },
            timeout=5
        )
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        logger.error(f"Turnstile verification error: {e}")
        # При помилці зв'язку з Cloudflare — пропускаємо (щоб не блокувати реальних юзерів)
        return True


def _is_rate_limited(request, limit=5, period=3600):
    """Перевіряє чи не перевищено ліміт відправок (5 за годину з одного IP)."""
    ip = _get_client_ip(request)
    cache_key = f'share_form_rate:{ip}'
    
    submissions = cache.get(cache_key, 0)
    if submissions >= limit:
        return True
    
    cache.set(cache_key, submissions + 1, period)
    return False


def _sanitize_input(text):
    """Видаляє HTML-теги з тексту для захисту від XSS."""
    if not isinstance(text, str):
        return ''
    return re.sub(r'<[^>]+>', '', text).strip()


# Максимальні довжини полів (відповідно до моделі Program)
_FIELD_MAX_LENGTHS = {
    'program_name': 200,
    'inviting_uni_text': 255,
    'inviting_uni_details': 2000,
    'home_uni_text': 255,
    'home_uni_details': 2000,
    'faculty': 100,
    'feedback': 5000,
    'user_name': 100,
    'faculty_details': 500,
    'level_details': 500,
}


def _validate_field_lengths(data):
    """Перевіряє чи не перевищено максимальну довжину полів."""
    for field, max_len in _FIELD_MAX_LENGTHS.items():
        value = data.get(field, '')
        if isinstance(value, str) and len(value) > max_len:
            return False, f'Поле занадто довге (максимум {max_len} символів)'
    return True, ''


# ============================================================
# SHARE PROGRAM VIEW (з 4-рівневим захистом)
# ============================================================

def share_program_page(request):
    if request.method == "POST":
        # Верхньорівневий try/except — щоб будь-яка необроблена помилка
        # повертала JSON, а не HTML-сторінку Django "Server Error (500)"
        try:
            return _handle_share_program_post(request)
        except Exception as e:
            logger.error(f"Unhandled error in share_program_page: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'Внутрішня помилка сервера. Спробуйте пізніше.'
            }, status=500)

    # GET — показати форму
    universities = University.objects.filter(is_approved=True).order_by('name_uk')
    context = {
        'universities': universities,
        'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
    }
    return render(request, 'share-my-program.html', context)


def _handle_share_program_post(request):
    """Обробка POST-запиту форми Share My Program (виділено для надійного error handling)."""
    client_ip = _get_client_ip(request)
    
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Невірний формат даних.'}, status=400)
    
    # ── РІВЕНЬ 1: Cloudflare Turnstile ──
    turnstile_token = data.get('cf_turnstile_token', '')
    if not _verify_turnstile(turnstile_token, client_ip):
        logger.warning(f"Turnstile verification failed from IP: {client_ip}")
        return JsonResponse({
            'status': 'error',
            'message': 'Перевірка безпеки не пройдена. Оновіть сторінку та спробуйте ще раз.'
        }, status=403)
    
    # ── РІВЕНЬ 2a: Honeypot ──
    # Якщо приховане поле "website" заповнене — це бот
    if data.get('website', ''):
        logger.warning(f"Honeypot triggered from IP: {client_ip}")
        # Повертаємо "успіх" щоб бот думав що все ок
        return JsonResponse({'status': 'success', 'message': 'Program added successfully'})
    
    # ── РІВЕНЬ 2b: Time-based check ──
    # Людина не може заповнити 8+ полів за 5 секунд
    form_loaded_at = data.get('form_loaded_at', 0)
    try:
        elapsed = (time.time() * 1000 - int(form_loaded_at)) / 1000  # секунди
        if elapsed < 5:
            logger.warning(f"Too fast submission ({elapsed:.1f}s) from IP: {client_ip}")
            return JsonResponse({'status': 'success', 'message': 'Program added successfully'})
    except (ValueError, TypeError):
        pass  # Якщо timestamp некоректний — пропускаємо перевірку
    
    # ── РІВЕНЬ 3: Серверна валідація ──
    is_valid, error_msg = _validate_field_lengths(data)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
    
    # ── РІВЕНЬ 4: Rate Limiting ──
    if _is_rate_limited(request, limit=5, period=3600):
        logger.warning(f"Rate limit exceeded from IP: {client_ip}")
        return JsonResponse({
            'status': 'error',
            'message': 'Ви відправили забагато заявок. Спробуйте через годину.'
        }, status=429)
    
    # ── Все перевірки пройдені — зберігаємо програму ──
    try:
        program = Program()
        program.name_uk = _sanitize_input(data.get('program_name', 'No Name'))
        
        # --- 1. Inviting University ---
        inviting_id = data.get('inviting_uni_id')
        inviting_text = _sanitize_input(data.get('inviting_uni_text', ''))
        inviting_details = _sanitize_input(data.get('inviting_uni_details', ''))
        
        if inviting_id == 'any':
            program.university = None
            program.university_details = "ОБРАНО: Будь-який університет / Any University.\n" + inviting_details
        elif inviting_id:
            try:
                program.university = University.objects.get(id=inviting_id)
                program.university_details = inviting_details
            except University.DoesNotExist:
                pass
        else:
            info_parts = []
            if inviting_text:
                info_parts.append(f"НОВА НАЗВА: {inviting_text}")
            if inviting_details:
                info_parts.append(f"ДЕТАЛІ: {inviting_details}")
            program.university_details = "\n\n".join(info_parts)

        # --- 2. Home University ---
        home_id = data.get('home_uni_id')
        home_text = _sanitize_input(data.get('home_uni_text', ''))
        home_details = _sanitize_input(data.get('home_uni_details', ''))
        
        if home_id == 'any':
            program.home_university = None
            program.home_university_details = "ОБРАНО: Будь-який університет / Any University.\n" + home_details
        elif home_id:
            try:
                program.home_university = University.objects.get(id=home_id)
                program.home_university_details = home_details
            except University.DoesNotExist:
                pass
        else:
            info_parts = []
            if home_text:
                info_parts.append(f"НОВА НАЗВА: {home_text}")
            if home_details:
                info_parts.append(f"ДЕТАЛІ: {home_details}")
            program.home_university_details = "\n\n".join(info_parts)

        # --- Інші поля ---
        program.faculty_uk = _sanitize_input(data.get('faculty', 'Other'))
        
        # Мапінг рівня навчання
        study_level_map = {
            'Bachelor': 'Bachelor',
            'Бакалавр': 'Bachelor',
            'Master': 'Master',
            'Магістр': 'Master',
            'PhD': 'PhD',
            'PhD / Аспірантура': 'PhD',
            'Other': 'Other',
            'Інше': 'Other'
        }
        raw_level = data.get('level', 'Other')
        program.study_level = study_level_map.get(raw_level, 'Other')
        
        program.description_uk = _sanitize_input(data.get('feedback', ''))
        program.submitted_by_name = _sanitize_input(data.get('user_name', ''))

        # --- Збереження деталей факультету та рівня ---
        admin_notes = []
        faculty_details = _sanitize_input(data.get('faculty_details', ''))
        level_details = _sanitize_input(data.get('level_details', ''))

        if faculty_details:
            admin_notes.append(f"Faculty details: {faculty_details}")
        if level_details:
            admin_notes.append(f"Level details: {level_details}")
        
        if admin_notes:
            program.user_university_text = " | ".join(admin_notes)[:255]
        
        program.save()
        logger.info(f"New program submitted: '{program.name_uk}' from IP: {client_ip}")
        return JsonResponse({'status': 'success', 'message': 'Program added successfully'})
        
    except Exception as e:
        logger.error(f"Error adding program: {e}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'Помилка при збереженні програми. Спробуйте ще раз.'}, status=400)