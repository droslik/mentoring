import pytest
from faker import Faker

from app.models import User, Book
from django.db import transaction
from django.core.exceptions import ValidationError


class TestBook:
    email = 'alex@authors.com'
    fake = Faker()

    @pytest.mark.django_db
    def test_create_book(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        user.clean_fields()
        user.save()
        book_factory(title=self.fake.name(), author=user)

        assert User.objects.count() == 1
        assert Book.objects.count() == 1

    @pytest.mark.django_db
    def test_empty_title_create_book(self, user_factory, book_factory):
        user_factory(email=self.email).clean_fields()
        assert User.objects.all().count() == 1
        user = User.objects.get(email=self.email)
        with pytest.raises(ValidationError) as exc:
            book = book_factory.build(author=user)
            book.clean_fields()
            book.save()
        assert user.books.all().count() == 0
        assert 'title' in exc.value.error_dict

    @pytest.mark.django_db
    def test_without_author_create_book(self, book_factory):
        with pytest.raises(ValueError) as exc:
            book = book_factory.build()
            book.clean_fields()
            book.save()

        assert 'author' in str(exc.value)

    @pytest.mark.django_db
    def test_string_author_field_create_book(self, book_factory):
        with pytest.raises(ValueError) as exc:
            book = book_factory.build(author=self.fake.name())
            book.clean_fields()
            book.save()

        assert 'author' in str(exc.value)

    @pytest.mark.django_db
    def test_not_saved_author_create_book(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        assert not User.objects.filter(id=user.id).exists()
        author = User.objects.filter(id=user.id).first()
        with pytest.raises(ValidationError) as exc:
            book = book_factory.build(author=author)
            book.clean_fields()
            book.save()
        assert 'author' in exc.value.error_dict

    @pytest.mark.django_db
    def test_fail_transaction_user_book_create_book(self, user_factory, book_factory):

        with pytest.raises(ValidationError) as exc:
            with transaction.atomic():
                user = user_factory.build(email=self.email)
                user.clean_fields()
                user.save()
                book = book_factory.build(author=user)
                book.clean_fields()
                book.save()
            assert 'title' in exc.value.error_dict
        assert not User.objects.filter(id=user.id).exists()
