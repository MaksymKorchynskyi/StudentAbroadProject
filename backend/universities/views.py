# backend/universities/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from urllib.parse import urlencode
from .models import University
from .serializers import UniversitySerializer, UniversityOptionsSerializer
from django_countries import countries as all_countries

# --- ДОДАЙТЕ ЦІ ІМПОРТИ ---
from django.shortcuts import render, get_object_or_404
from programs.models import Program  # Імпорт моделі Program для пошуку зв'язків
# --------------------------

class UniversityListView(generics.ListAPIView):
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = University.objects.filter(is_approved=True)
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name_uk__icontains=search) | 
                Q(name_en__icontains=search) |
                Q(description_uk__icontains=search) |
                Q(description_en__icontains=search) |
                Q(location_uk__icontains=search) |
                Q(location_en__icontains=search))
        return queryset.order_by('name_uk')

class UniversityDetailView(generics.RetrieveAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]

class UniversityCreateView(generics.CreateAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [IsAdminUser]  # Тільки адміни можуть створювати університети

class UniversityOptionsView(generics.ListAPIView):
    serializer_class = UniversityOptionsSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return University.objects.filter(is_approved=True).order_by('name_uk')

def university_page_view(request, slug=None):
    """
    View для відображення HTML сторінки університету.
    - Slug-based URLs (/university/<slug>/) render the page directly
    - Legacy URLs (?id=X) do 301 redirect to slug URL (preserving query params)
    """
    # Handle legacy ?id= parameter with 301 redirect
    if not slug:
        uni_id = request.GET.get('id')
        if uni_id:
            university = get_object_or_404(University, pk=uni_id)
            
            # Build redirect URL with preserved query params (except 'id')
            redirect_url = university.get_absolute_url()
            
            # Preserve other query params for marketing tracking
            query_params = request.GET.copy()
            query_params.pop('id', None)  # Remove 'id' param
            if query_params:
                redirect_url = f"{redirect_url}?{urlencode(query_params)}"
            
            return HttpResponsePermanentRedirect(redirect_url)
        else:
            # No slug and no id - return empty context
            return render(request, 'uni-read-more.html', {})
    
    # Slug-based URL - render the page
    university = get_object_or_404(University, slug=slug, is_approved=True)
    
    # Шукаємо програми з оптимізацією
    programs = Program.objects.filter(
        Q(university=university) | Q(home_university=university),
        is_approved=True
    ).select_related('university', 'home_university').distinct().order_by('-created_at')
    
    # SEO Meta - dynamic from university data
    uni_name = university.name_en or university.name_uk or 'University'
    description = (university.description_en or university.description_uk or '')[:160]
    
    # Fallback if description is empty
    if not description:
        description = f"Explore exchange programs at {uni_name}. Find details about study opportunities and student experiences."
    
    context = {
        'university': university,
        'programs': programs,
        # SEO Meta
        'meta_title': f'{uni_name} | StudentAbroad',
        'meta_description': description,
        'og_type': 'article',
        # Breadcrumbs for SEO
        'breadcrumbs': [
            {'name': 'Home', 'name_uk': 'Головна', 'url': '/'},
            {'name': 'Universities', 'name_uk': 'Університети', 'url': '/uni-list.html'},
            {'name': uni_name, 'name_uk': university.name_uk or uni_name, 'url': university.get_absolute_url()},
        ],
    }
    
    return render(request, 'uni-read-more.html', context)

def university_list_page(request):
    """
    View для відображення сторінки списку університетів.
    """
    # Отримуємо всі затверджені університети
    universities = University.objects.filter(is_approved=True).order_by('name_uk')
    
    # Збираємо унікальні коди країн
    used_country_codes = set(universities.values_list('country', flat=True))
    
    # Формуємо список словників для шаблону з назвами обома мовами
    from django.utils import translation
    countries_data = []
    
    # Створюємо словники лише один раз
    with translation.override('en'):
        en_dict = dict(all_countries)
    with translation.override('uk'):
        uk_dict = dict(all_countries)
        
    for code in used_country_codes:
        if not code:
            continue
            
        countries_data.append({
            'code': code,
            'name_en': en_dict.get(code, code),
            'name_uk': uk_dict.get(code, code)
        })
    
    # Сортуємо список країн за українською назвою
    countries_data.sort(key=lambda x: x['name_uk'])

    context = {
        'universities': universities,
        'countries': countries_data,
        # SEO Meta
        'meta_title': 'Universities | StudentAbroad',
        'meta_title_uk': 'Університети | StudentAbroad',
        'meta_description': 'Browse partner universities offering exchange programs. Find the right institution for your study abroad experience.',
        'meta_description_uk': 'Переглядай університети-партнери з програмами обміну. Знайди потрібний заклад для навчання за кордоном.',
    }
    
    return render(request, 'uni-list.html', context)