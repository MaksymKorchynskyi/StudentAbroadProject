# backend/config/context_processors.py
"""
SEO Context Processors for StudentAbroad
Provides default meta tags and SEO data to all templates.
"""


def seo_defaults(request):
    """
    Adds default SEO metadata to template context.
    Individual views can override these values.
    """
    return {
        'default_meta_title': 'StudentAbroad - Study Abroad Programs for Ukrainian Students',
        'default_meta_title_uk': 'StudentAbroad - Програми навчання за кордоном для українських студентів',
        'default_meta_description': 'Browse exchange programs, universities, and study abroad opportunities for Ukrainian students. Get honest reviews and insights directly from other students.',
        'default_meta_description_uk': 'Переглядай програми обміну, університети та можливості навчання за кордоном для українських студентів. Отримуй чесні відгуки та поради від інших студентів.',
        'default_og_image': request.build_absolute_uri('/static/project/img/bg.png'),
        'site_name': 'StudentAbroad',
        'canonical_url': request.build_absolute_uri(request.path),
    }
