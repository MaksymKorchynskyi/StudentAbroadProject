from django.contrib import admin
from django import forms
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from .models import Program


@admin.register(Program)
class ProgramAdmin(ModelAdmin):
    """
    Unfold-based admin for Program model.
    Preserves all existing functionality with modern UI and custom actions.
    """
    list_display = (
        'name_uk', 
        'university', 
        'home_university', 
        'faculty_uk',
        'is_approved',
        'display_approved_badge',
        'created_at'
    )
    
    list_filter = ('is_approved', 'program_type', 'study_level', 'faculty_uk')
    
    search_fields = (
        'name_uk', 
        'name_en', 
        'university__name_uk', 
        'home_university__name_uk',
        'university_details',
        'home_university_details',
        'faculty_details',
        'level_details'
    )
    
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
    
    # Performance optimization for large datasets
    list_select_related = ('university', 'home_university')
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name_uk', 'name_en', 'slug', 'is_approved')
        }),
        
        ('Університет Прийому', {
            'fields': (
                'university',          
                'university_details'   
            ),
            'description': "Якщо поле 'Університет' пусте або обрано невірне, перевірте 'Інформація про університет'."
        }),
        
        ('Домашній Університет', {
            'fields': (
                'home_university',
                'home_university_details'
            )
        }),

        ('Факультет та Рівень', {
            'fields': ('faculty_uk', 'faculty_en', 'faculty_details',
                       'study_level', 'level_details', 'program_type'),
            'description': "Якщо користувач натиснув '+', його коментар буде в полях 'Деталі...'."
        }),
        
        ('Опис та Відгук', {
            'fields': ('description_uk', 'description_en', 'testimonial_uk', 'testimonial_en')
        }),
        
        ('Корисні посилання', {
            'fields': (
                'useful_link_1', 'useful_link_1_title_uk', 'useful_link_1_title_en',
                'useful_link_2', 'useful_link_2_title_uk', 'useful_link_2_title_en',
                'useful_link_3', 'useful_link_3_title_uk', 'useful_link_3_title_en'
            ),
            'classes': ('collapse',)
        }),
        
        ('Інформація про заявника', {
            'fields': ('submitted_by_name', 'submitted_by_email', 'created_at', 'updated_at')
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
    def display_approved_badge(self, obj):
        return obj.is_approved, "Опубліковано" if obj.is_approved else "Чернетка"



    # ============================================================
    # CUSTOM ACTIONS - CRM Functionality
    # ============================================================
    
    actions = ['make_approved', 'make_draft', 'duplicate_program']
    
    @action(description="✅ Опублікувати вибрані")
    def make_approved(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"✅ Опубліковано {count} програм(и)")

    @action(description="📝 Перевести у чернетки")
    def make_draft(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"📝 Переведено у чернетки {count} програм(и)")

    @action(description="📋 Дублювати програму")
    def duplicate_program(self, request, queryset):
        for program in queryset:
            program.pk = None
            program.slug = ''  # Will auto-generate
            program.name_uk = f"[КОПІЯ] {program.name_uk}"
            program.name_en = f"[COPY] {program.name_en}" if program.name_en else ''
            program.is_approved = False
            program.save()
        self.message_user(request, f"📋 Продубльовано {queryset.count()} програм(и)")