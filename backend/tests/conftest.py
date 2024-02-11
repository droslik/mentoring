import pytest
from unittest.mock import MagicMock
from .factories import UserFactory, BookFactory


@pytest.fixture()
def user_factory():
    def create_user():
        return UserFactory
    yield create_user()


@pytest.fixture()
def book_factory(user_factory):
    def create_book():
        return BookFactory
    yield create_book()


@pytest.fixture()
def mock_requests():
    requests = MagicMock()
    return requests.get()
