from pytest_factoryboy import register

from .factories import UserFactory, BookFactory

register(UserFactory)
register(BookFactory)
