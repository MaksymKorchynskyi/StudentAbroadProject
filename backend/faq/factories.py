import factory
import random
from faker import Faker
from faq.models import FAQCategory, FAQItem

fake = Faker('uk_UA')
fake_en = Faker('en_US')

class FAQCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQCategory

    name_ua = factory.Faker('word', locale='uk_UA')
    name_en = factory.Faker('word', locale='en_US')


class FAQItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FAQItem

    question_ua = factory.LazyAttribute(lambda _: f"{fake.sentence().rstrip('.')}?")
    question_en = factory.LazyAttribute(lambda _: f"{fake_en.sentence().rstrip('.')}?")
    
    answer_ua = factory.Faker('paragraph', nb_sentences=4, locale='uk_UA')
    answer_en = factory.Faker('paragraph', nb_sentences=4, locale='en_US')
    
    author_ua = factory.Faker('name', locale='uk_UA')
    author = factory.Faker('name', locale='en_US')
    
    editor_ua = factory.Faker('name', locale='uk_UA')
    editor = factory.Faker('name', locale='en_US')
    
    is_published = True

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            # Якщо не передано конкретних категорій, додамо випадкові 1-2 існуючі категорії
            all_categories = list(FAQCategory.objects.all())
            if all_categories:
                # Беремо від 1 до 2 випадкових категорій
                chosen = random.sample(all_categories, k=random.randint(1, min(2, len(all_categories))))
                for cat in chosen:
                    self.categories.add(cat)
