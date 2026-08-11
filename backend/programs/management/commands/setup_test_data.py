import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from universities.models import University
from programs.models import Program
from universities.factories import UniversityFactory
from programs.factories import ProgramFactory
from faq.models import FAQCategory, FAQItem
from faq.factories import FAQCategoryFactory, FAQItemFactory

class Command(BaseCommand):
    help = "Генерує масив тестових даних (університети, програми, користувачі)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # ЗАПОБІЖНИК: Ніколи не запускати на продакшені!
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("ПОМИЛКА: Не можна генерувати тестові дані на продакшені (DEBUG=False)!"))
            return

        self.stdout.write(self.style.WARNING("Видалення старих даних..."))
        Program.objects.all().delete()
        University.objects.all().delete()
        FAQItem.objects.all().delete()
        FAQCategory.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Створення тестових користувачів...")
        if not User.objects.filter(username='content_maker').exists():
            User.objects.create_user('content_maker', 'content@test.com', 'testpassword123')

        self.stdout.write("Генерація Університетів (50 шт)...")
        # Створюємо 50 університетів
        universities = UniversityFactory.create_batch(50)

        self.stdout.write("Генерація Програм (200 шт)...")
        # Створюємо 200 програм, призначаючи випадкові університети
        for _ in range(200):
            ProgramFactory.create(
                university=random.choice(universities),
                home_university=random.choice(universities)
            )

        self.stdout.write("Генерація FAQ Категорій (5 шт)...")
        FAQCategoryFactory.create_batch(5)

        self.stdout.write("Генерація FAQ Питань (30 шт)...")
        # Оскільки ми прописали @factory.post_generation в FAQItemFactory, 
        # фабрика сама прив'яже випадкові категорії під час створення
        FAQItemFactory.create_batch(30)

        self.stdout.write(self.style.SUCCESS("✅ Успішно згенеровано тестові дані! (50 універів, 200 програм, 30 FAQ)"))
