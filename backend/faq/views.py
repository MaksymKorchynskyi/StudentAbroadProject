from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.exceptions import ObjectDoesNotExist
import json
import logging
from .models import FAQItem, FAQCategory
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import FAQSerializer

logger = logging.getLogger(__name__)

@require_GET
def faq_list(request):
    try:
        lang = request.GET.get('lang', 'en')
        
        # Перевіряємо чи підтримується мова (додаємо підтримку 'uk' як альтернативи 'ua')
        if lang not in ['en', 'ua', 'uk']:
            lang = 'en'
        # Якщо використовується 'uk', змінюємо на 'ua' для зворотньої сумісності
        if lang == 'uk':
            lang = 'ua'
        
        # Фільтруємо тільки опубліковані FAQ
        faq_items = FAQItem.objects.filter(is_published=True).order_by('-created_at')
        
        result = []
        for item in faq_items:
            categories = []
            for category in item.categories.all():
                categories.append({
                    'id': category.id,
                    'name': getattr(category, f'name_{lang}', category.name_en)
                })
            
            result.append({
                'id': item.id,
                'question': getattr(item, f'question_{lang}', item.question_en),
                'answer': getattr(item, f'answer_{lang}', item.answer_en),
                'categories': categories,
                'author': getattr(item, f'author_{lang}', item.author),
                'editor': getattr(item, f'editor_{lang}', item.editor),
                'created_at': item.created_at.strftime('%d/%m/%Y'),
                'updated_at': item.updated_at.strftime('%d/%m/%Y')
            })
        
        response = JsonResponse({'faq_items': result, 'status': 'success', 'language': lang})
        # CORS керується через django-cors-headers middleware (settings.py)
        return response
        
    except Exception as e:
        logger.error(f"Error fetching FAQ items: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'Помилка при завантаженні FAQ',
            'faq_items': []
        }, status=500)
    
# API View (для мобільних додатків або AJAX, якщо потрібно)
class FAQListView(generics.ListAPIView):
    # Використовуємо FAQItem та фільтруємо по is_published
    queryset = FAQItem.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

# View для HTML сторінки (те, що ми підключили в urls.py)
def faq_page_view(request):
    """
    View для відображення HTML сторінки FAQ.
    """
    # Додано prefetch_related('categories') для оптимізації
    faqs = FAQItem.objects.filter(is_published=True).order_by('-created_at').prefetch_related('categories')
    
    context = {
        'faqs': faqs,
        # SEO Meta
        'meta_title': 'FAQ - Frequently Asked Questions | StudentAbroad',
        'meta_title_uk': 'FAQ - Часті питання | StudentAbroad',
        'meta_description': 'Get answers to common questions about studying abroad, exchange programs, and application processes.',
        'meta_description_uk': 'Отримай відповіді на поширені питання про навчання за кордоном, програми обміну та процес подачі документів.',
    }
    
    return render(request, 'faq.html', context)