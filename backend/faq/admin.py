from django.conf import settings
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from .models import FAQCategory, FAQItem


@admin.register(FAQCategory)
class FAQCategoryAdmin(ModelAdmin):
    """
    Unfold-based admin for FAQ Category model.
    """
    list_display = ('name_en', 'name_ua', 'display_faq_count')
    search_fields = ('name_en', 'name_ua')
    
    def display_faq_count(self, obj):
        count = obj.faqitem_set.count()
        return f"{count} питань"
    display_faq_count.short_description = 'Кількість FAQ'


@admin.register(FAQItem)
class FAQItemAdmin(ModelAdmin):
    """
    Unfold-based admin for FAQ Item model.
    Preserves all existing functionality with modern UI.
    """
    list_display = (
        'question_en', 
        'question_ua', 
        'is_published',
        'display_published_badge',
        'display_categories', 
        'created_at', 
        'updated_at'
    )
    list_filter = ('categories', 'created_at', 'is_published')
    search_fields = ('question_en', 'question_ua', 'answer_en', 'answer_ua', 'author', 'author_ua')
    list_editable = ('is_published',)
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('English Content', {
            'fields': ('question_en', 'answer_en', 'author', 'editor')
        }),
        ('Ukrainian Content', {
            'fields': ('question_ua', 'answer_ua', 'author_ua', 'editor_ua')
        }),
        ('Categories and Metadata', {
            'fields': ('categories', 'is_published', 'created_at', 'updated_at')
        }),
    )
        
    # Custom display with Unfold badges
    @display(
        description="Статус",
        label={
            True: "success",
            False: "warning",
        }
    )
    def display_published_badge(self, obj):
        return obj.is_published, "Опубліковано" if obj.is_published else "Чернетка"
    
    def display_categories(self, obj):
        categories = obj.categories.all()
        if categories:
            return ", ".join([cat.name_en for cat in categories])
        return "—"
    display_categories.short_description = 'Categories'
    
    # ============================================================
    # CUSTOM ACTIONS
    # ============================================================
    
    actions = ['publish_selected', 'unpublish_selected']
    
    @action(description="✅ Опублікувати вибрані FAQ")
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"✅ Опубліковано {count} FAQ")
    
    @action(description="📝 Приховати вибрані FAQ")
    def unpublish_selected(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"📝 Приховано {count} FAQ")