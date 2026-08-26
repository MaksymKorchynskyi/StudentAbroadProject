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
    
    @factory.lazy_attribute
    def answer_ua(self):
        if random.choice([True, False]):
            return "\n\n".join(fake.paragraphs(nb=random.randint(2, 5)))
        return fake.paragraph(nb_sentences=random.randint(8, 15))

    @factory.lazy_attribute
    def answer_en(self):
        if random.choice([True, False]):
            return "\n\n".join(fake_en.paragraphs(nb=random.randint(2, 5)))
        return fake_en.paragraph(nb_sentences=random.randint(8, 15))
    
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
