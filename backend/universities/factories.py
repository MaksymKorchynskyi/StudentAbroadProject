import factory
from faker import Faker
from universities.models import University

fake = Faker('uk_UA')

class UniversityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = University

    # Генеруємо реалістичні дані
    name_uk = factory.LazyAttribute(lambda _: f"{fake.company()} Університет")
    name_en = factory.LazyAttribute(lambda _: f"{fake.company()} University")
    
    country = factory.Faker('country_code')
    location_uk = factory.Faker('city')
    location_en = factory.Faker('city', locale='en_US')
    
    description_uk = factory.Faker('text', max_nb_chars=500)
    description_en = factory.Faker('text', max_nb_chars=500, locale='en_US')
    
    contact_email = factory.Faker('company_email')
    website_url = factory.Faker('url')
    
    additional_info_uk = factory.Faker('text', max_nb_chars=300)
    additional_info_en = factory.Faker('text', max_nb_chars=300, locale='en_US')
    
    # Картинки не генеруємо, щоб не засмічувати Cloudflare R2 бакет. 
    # В моделі University поля logo та background_image мають blank=True, null=True, тому це безпечно.
    logo = None
    background_image = None
    
    is_approved = True
