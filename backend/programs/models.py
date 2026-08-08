from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from universities.models import University
import uuid

class Program(models.Model):
    STUDY_LEVEL_CHOICES = [
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
        ('PhD', 'PhD'),
        ('Other', 'Other'),
    ]
    PROGRAM_TYPE_CHOICES = [
        ('exchange', 'Exchange Program'),
        ('degree', 'Degree Program'),
        ('short_term', 'Short-term Program'),
    ]

    name_uk = models.CharField(max_length=200, verbose_name="Назва програми")
    name_en = models.CharField(max_length=200, verbose_name="Program name (eng)", blank=True)
    
    # SEO: Human-readable URL slug
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="URL Slug",
        help_text="Автоматично генерується з назви"
    )
    
    university = models.ForeignKey(
        University, 
        on_delete=models.SET_NULL, 
        related_name='host_programs', 
        verbose_name="Університет прийому (з бази)",
        null=True, 
        blank=True
    )
    
    # Це поле використовуємо для всіх нотаток (назва нового, деталі з плюсика)
    university_details = models.TextField(
        blank=True, 
        verbose_name="Інформація про університет / Нова назва"
    )
    # Технічне поле, щоб не ламати старі міграції (можна ігнорувати)
    university_text = models.CharField(max_length=255, blank=True, verbose_name="Legacy Text")

    home_university = models.ForeignKey(
        University, 
        on_delete=models.SET_NULL, 
        related_name='home_programs',
        verbose_name="Університет відправлення (з бази)",
        null=True,
        blank=True
    )
    
    # Це поле використовуємо для всіх нотаток
    home_university_details = models.TextField(
        blank=True, 
        verbose_name="Інформація про дом. університет / Нова назва"
    )
    home_university_text = models.CharField(max_length=255, blank=True, verbose_name="Legacy Text")

    # Решта полів
    user_university_text = models.CharField(max_length=255, blank=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, default='exchange')
    faculty_uk = models.CharField(max_length=100, verbose_name="Факультет")
    faculty_en = models.CharField(max_length=100, blank=True, verbose_name="Faculty (eng)")
    
    # ВИПРАВЛЕНО: Додано choices=STUDY_LEVEL_CHOICES
    study_level = models.CharField(max_length=50, choices=STUDY_LEVEL_CHOICES, verbose_name="Рівень навчання") 
    
    description_uk = models.TextField(blank=True, default='', verbose_name="Опис (укр)")
    description_en = models.TextField(blank=True, default='', verbose_name="Description (eng)")
    testimonial_uk = models.TextField(blank=True, default='', verbose_name="Відгук (укр)")
    testimonial_en = models.TextField(blank=True, default='', verbose_name="Testimonial (eng)")
    
    useful_link_1 = models.URLField(blank=True, null=True, verbose_name="Корисне посилання 1")
    useful_link_2 = models.URLField(blank=True, null=True, verbose_name="Корисне посилання 2")
    useful_link_3 = models.URLField(blank=True, null=True, verbose_name="Корисне посилання 3")
    useful_link_1_title_uk = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 1 (укр)")
    useful_link_2_title_uk = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 2 (укр)")
    useful_link_3_title_uk = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 3 (укр)")
    useful_link_1_title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 1 (eng)")
    useful_link_2_title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 2 (eng)")
    useful_link_3_title_en = models.CharField(max_length=100, blank=True, null=True, verbose_name="Назва посилання 3 (eng)")
    
    is_approved = models.BooleanField(default=False, db_index=True, verbose_name="Опубліковано")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_by_name = models.CharField(max_length=100, blank=True, default='', verbose_name="Ім'я заявника")
    submitted_by_email = models.EmailField(blank=True, default='', verbose_name="Email заявника")

    def __str__(self):
        return f"{self.name_uk} (Draft: {not self.is_approved})"

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            # Use English name if available, otherwise Ukrainian
            base_name = self.name_en if self.name_en else self.name_uk
            base_slug = slugify(base_name, allow_unicode=True)
            
            # Ensure uniqueness by appending short UUID if needed
            if not base_slug:
                base_slug = 'program'
            
            unique_slug = base_slug
            counter = 1
            while Program.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns canonical URL for SEO sitemaps"""
        return reverse('program-detail', kwargs={'slug': self.slug})

    def get_useful_links_combined(self):
        links = []
        for i in range(1, 4):
            url = getattr(self, f'useful_link_{i}', None)
            if url:
                t_en = getattr(self, f'useful_link_{i}_title_en', '')
                t_uk = getattr(self, f'useful_link_{i}_title_uk', '')
                final_en = t_en if t_en else (t_uk if t_uk else f'Useful link {i}')
                final_uk = t_uk if t_uk else (t_en if t_en else f'Корисне посилання {i}')
                links.append({'url': url, 'title_en': final_en, 'title_uk': final_uk})
        return links

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', '-created_at']),
        ]