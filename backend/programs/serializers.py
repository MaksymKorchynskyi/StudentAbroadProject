# backend/programs/serializers.py
from rest_framework import serializers
from .models import Program
from universities.models import University

class ProgramSerializer(serializers.ModelSerializer):
    university = serializers.StringRelatedField(read_only=True)
    
    # Поля для запису (Write Only)
    university_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    home_university_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    university_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    home_university_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    university_details = serializers.CharField(write_only=True, required=False, allow_blank=True)
    home_university_details = serializers.CharField(write_only=True, required=False, allow_blank=True)

    useful_links = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            'id', 'name_uk', 'name_en',
            'university', 'university_id', 'university_name', 'university_details',
            'home_university', 'home_university_id', 'home_university_name', 'home_university_details',
            'program_type', 'study_level', 
            'faculty_uk', 'faculty_en',
            'description_uk', 'description_en',
            'testimonial_uk', 'testimonial_en',
            'submitted_by_name', 'submitted_by_email', 
            'faculty_details', 'level_details', 'useful_links', 
            'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'is_approved']

    def get_useful_links(self, obj):
        return obj.get_useful_links_combined()

    def validate(self, data):
        """
        Перевірка наявності університету.
        Потрібно або university_id, або university_name.
        """
        uni_id = data.get('university_id')
        uni_name = data.get('university_name')

        if not uni_id and not uni_name:
            raise serializers.ValidationError({"university": "Необхідно вибрати університет зі списку або ввести назву нового."})
        
        return data

    def create(self, validated_data):
        university_name = validated_data.pop('university_name', None)
        home_university_name = validated_data.pop('home_university_name', None)
        university_id = validated_data.pop('university_id', None)
        home_university_id = validated_data.pop('home_university_id', None)
        
        uni_details = validated_data.pop('university_details', '')
        home_uni_details = validated_data.pop('home_university_details', '')

        validated_data['faculty_details'] = uni_details
        validated_data['level_details'] = ''

        # Логіка Приймаючого університету
        if university_id:
            validated_data['university_id'] = university_id
        elif university_name:
            new_uni = University.objects.create(
                name_uk=university_name,
                name_en=university_name,
                is_approved=False,
                country='UA', # Адмін змінить
                additional_info_uk=uni_details
            )
            validated_data['university'] = new_uni

        # Логіка Домашнього університету
        if home_university_id:
            validated_data['home_university_id'] = home_university_id
        elif home_university_name:
            new_home_uni = University.objects.create(
                name_uk=home_university_name,
                name_en=home_university_name,
                is_approved=False,
                country='UA',
                additional_info_uk=home_uni_details
            )
            validated_data['home_university'] = new_home_uni

        validated_data['is_approved'] = False
        return super().create(validated_data)