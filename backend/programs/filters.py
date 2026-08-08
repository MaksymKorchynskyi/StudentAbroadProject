import django_filters
from .models import Program


class ProgramFilter(django_filters.FilterSet):
    study_level = django_filters.MultipleChoiceFilter(
        choices=Program.STUDY_LEVEL_CHOICES
    )
    program_type = django_filters.MultipleChoiceFilter(
        choices=Program.PROGRAM_TYPE_CHOICES
    )

    class Meta:
        model = Program
        fields = {
            'university': ['exact'],
            'study_level': ['exact'],
            'program_type': ['exact'],
        }