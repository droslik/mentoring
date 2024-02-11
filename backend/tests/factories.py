import factory

from app import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = 'alex'
    email = 'alex@alex.com'
    password = 'alex'


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book
    title = 'new_book'
    author = factory.SubFactory(UserFactory)
    short_description = 'Very interesting book'
