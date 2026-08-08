from django.db import models
from django.utils import timezone

class FAQCategory(models.Model):
    name_en = models.CharField(max_length=100, verbose_name="Category name (English)")
    name_ua = models.CharField(max_length=100, verbose_name="Назва категорії (Українська)")
    
    def __str__(self):
        return self.name_en

class FAQItem(models.Model):
    question_en = models.CharField(max_length=255, verbose_name="Question (English)")
    question_ua = models.CharField(max_length=255, verbose_name="Питання (Українська)")
    answer_en = models.TextField(verbose_name="Answer (English)")
    answer_ua = models.TextField(verbose_name="Відповідь (Українська)")
    categories = models.ManyToManyField(FAQCategory)
    author = models.CharField(max_length=100, verbose_name="Author (English)")
    author_ua = models.CharField(max_length=100, verbose_name="Автор (Українська)")
    editor = models.CharField(max_length=100, verbose_name="Editor (English)")
    editor_ua = models.CharField(max_length=100, verbose_name="Редактор (Українська)")
    is_published = models.BooleanField(default=False, db_index=True, verbose_name="Опубліковано")  # Додано поле публікації
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question_en