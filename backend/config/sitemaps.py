# backend/config/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from programs.models import Program
from universities.models import University



class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return ['index', 'program-list', 'uni-list', 'faq']
    
    def location(self, item):
        return reverse(item)


class ProgramSitemap(Sitemap):
    """Sitemap for program detail pages - uses SEO-friendly slug URLs"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Program.objects.filter(is_approved=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        # Use model's get_absolute_url for SEO-friendly slug-based URLs
        return obj.get_absolute_url()


class UniversitySitemap(Sitemap):
    """Sitemap for university detail pages - uses SEO-friendly slug URLs"""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return University.objects.filter(is_approved=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        # Use model's get_absolute_url for SEO-friendly slug-based URLs
        return obj.get_absolute_url()

