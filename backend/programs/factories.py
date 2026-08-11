import factory
import random
from programs.models import Program
from universities.factories import UniversityFactory

class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program

    name_uk = factory.Faker('sentence', nb_words=4)
    name_en = factory.Faker('sentence', nb_words=4, locale='en_US')
    
    # Автоматично створює університети-партнери
    university = factory.SubFactory(UniversityFactory)
    home_university = factory.SubFactory(UniversityFactory)
    
    study_level = factory.LazyFunction(lambda: random.choice(['Bachelor', 'Master', 'PhD', 'Other']))
    program_type = factory.LazyFunction(lambda: random.choice(['exchange', 'degree', 'short_term']))
    
    faculty_uk = factory.Faker('job')
    faculty_en = factory.Faker('job', locale='en_US')
    
    description_uk = factory.Faker('text', max_nb_chars=350)
    description_en = factory.Faker('text', max_nb_chars=350, locale='en_US')
    
    testimonial_uk = factory.Faker('paragraph', nb_sentences=10)
    testimonial_en = factory.Faker('paragraph', nb_sentences=10, locale='en_US')
    
    useful_link_1 = factory.Faker('url')
    useful_link_1_title_uk = factory.Faker('word')
    
    submitted_by_name = factory.Faker('name')
    submitted_by_email = factory.Faker('email')
    
    is_approved = True
