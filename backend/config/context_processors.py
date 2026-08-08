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
        'default_meta_description': 'Find exchange programs, universities, and study abroad opportunities. Get honest reviews from international students.',
        'default_meta_description_uk': 'Знайди програми обміну, університети та можливості навчання за кордоном. Отримай чесні відгуки від міжнародних студентів.',
        'default_og_image': request.build_absolute_uri('/static/project/img/bg.png'),
        'site_name': 'StudentAbroad',
        'canonical_url': request.build_absolute_uri(),
    }
