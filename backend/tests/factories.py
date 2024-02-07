import factory

from app import models

from django.core.validators import EmailValidator
from django.db.models import EmailField


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = 'alex'
    email = EmailField(validators=[EmailValidator], blank=False, null=False)
    password = 'alex'


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Book

    author = UserFactory
