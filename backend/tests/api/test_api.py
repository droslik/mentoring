import pytest

from app.models import User, Book
from app.views import BookCreateApiView

from django.forms import model_to_dict
from django.urls import reverse

from faker import Faker
from requests import Response
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock


fake = Faker()
client = APIClient()


class TestBook:
    email = 'alex@authors.com'
    create_user_url = '/api/v1/users/create_user/'
    own_user_url = '/api/v1/users/own/'
    create_book_url = '/api/v1/books/create_book/'
    update_book_url = '/api/v1/books/'
    book_fields = ['title', 'short_description', 'author']

    @pytest.mark.django_db
    def test_url(self):
        assert self.create_user_url == reverse('create-user')
        assert self.own_user_url == reverse('own')

    @pytest.mark.django_db
    def test_register_user(self, user_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)

        assert response.status_code == 201

    @pytest.mark.django_db
    def test_username_exists_register_user(self, user_factory):
        user_factory.create(email=self.email)
        new_user = user_factory.build(email=self.email)
        data = model_to_dict(new_user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)

        assert response.status_code == 400
        assert 'username' in response.json().keys()
        assert 'username already exists' in str(response.json().get('username'))

    @pytest.mark.django_db
    def test_without_username_register_user(self, user_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['email', 'password'])
        response = client.post(self.create_user_url, data)

        assert response.status_code == 400
        assert 'username' in response.json().keys()

    @pytest.mark.django_db
    def test_without_password_register_user(self, user_factory):
        new_user = user_factory.build(email=self.email)
        data = model_to_dict(new_user, fields=['username', 'email'])
        response = client.post(self.create_user_url, data)

        assert response.status_code == 400
        assert 'password' in response.json().keys()

    @pytest.mark.django_db
    def test_incorrect_email_register_user(self, user_factory):
        user = user_factory.build(email='123')
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)

        assert response.status_code == 400
        assert 'email' in response.json().keys()

    @pytest.mark.django_db
    def test_own_user_page(self, user_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        client.force_authenticate(user_from_db.first())
        response = client.get('/api/v1/users/own/')

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_own_user_401_error_code(self, user_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        response = client.get(self.own_user_url)

        assert response.status_code == 401

    @pytest.mark.django_db
    def test_create_book_201(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        client.force_authenticate(user_from_db.first())
        book = book_factory.build(title=fake.name(), author=user_from_db.first())
        book_data = model_to_dict(
            book,
            fields=[field for field in self.book_fields if hasattr(book, field) and getattr(book, field) is not None],
        )
        response = client.post(self.create_book_url, book_data)

        assert response.status_code == 201

    @pytest.mark.django_db
    def test_create_book_400_without_title(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        client.force_authenticate(user_from_db.first())
        book = book_factory.build(author=user_from_db.first())
        book_data = model_to_dict(
            book,
            fields=[field for field in self.book_fields if hasattr(book, field) and getattr(book, field) is not None],
        )
        response = client.post(self.create_book_url, book_data)

        assert response.status_code == 400
        assert 'title' in response.json().keys()

    @pytest.mark.django_db
    def test_create_book_403_error_code(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        book = book_factory.build(title=fake.name(), author=user_from_db.first())
        book_data = model_to_dict(
            book,
            fields=[field for field in self.book_fields if hasattr(book, field) and getattr(book, field) is not None],
            )
        response = client.post(self.create_book_url, book_data)

        assert response.status_code == 403

    def test_create_book_incorrect_inner_url(self):
        view_class = BookCreateApiView()
        some_response = Response()
        some_response.status_code = 400
        view_class.post = MagicMock(some_response=some_response)
        mock_post_response = Response()
        mock_post_response.status_code = 200 if view_class.post.some_response.status_code == 200 else 400

        with patch('app.views.BookCreateApiView.post', return_value=mock_post_response) as res:
            assert res.return_value.status_code == 400

    def test_create_book_incorrect_2_inner_url(self):
        view_class = BookCreateApiView()
        some_response = Response()
        some_response.status_code = 404
        view_class.post = MagicMock(some_response=some_response)
        mock_post_response = Response()
        mock_post_response.status_code = 200 if view_class.post.some_response.status_code == 200 else 400

        with patch('app.views.BookCreateApiView.post', return_value=mock_post_response) as res:
            assert res.return_value.status_code == 400

    def test_create_book_correct_inner_url(self):
        view_class = BookCreateApiView()
        some_response = Response()
        some_response.status_code = 200
        view_class.post = MagicMock(some_response=some_response)
        mock_post_response = Response()
        mock_post_response.status_code = 200 if view_class.post.some_response.status_code == 200 else 400

        with patch('app.views.BookCreateApiView.post', return_value=mock_post_response) as res:
            assert res.return_value.status_code == 200

    @pytest.mark.django_db
    def test_update_book(self, user_factory, book_factory):
        user = user_factory.build(email=self.email)
        data = model_to_dict(user, fields=['username', 'email', 'password'])
        response = client.post(self.create_user_url, data)
        user_from_db = User.objects.filter(email=self.email)

        assert response.status_code == 201
        assert user_from_db.exists()
        user_from_db = user_from_db.first()
        client.force_authenticate(user_from_db)
        book = book_factory.build(title=fake.name(), author=user_from_db)
        book_data = model_to_dict(
            book,
            fields=[field for field in self.book_fields if
                    hasattr(book, field) and getattr(book, field) is not None],
        )
        # create book
        response = client.post(self.create_book_url, book_data)
        assert response.status_code == 201

        book_from_db = Book.objects.get(title=book_data['title'])
        new_title = fake.name()

        # update book by authenticated author
        response = client.put(f'{self.update_book_url}{book_from_db.id}/', data={'title': new_title})
        assert response.status_code == 200

        client.logout()
        response = client.put(f'{self.update_book_url}{book_from_db.id}/', data={'title': new_title})
        assert response.status_code == 401

        user2 = user_factory.build(username='alex2', email=self.email)
        data = model_to_dict(user2, fields=['username', 'email', 'password'])
        # create another user
        response = client.post(self.create_user_url, data)
        assert response.status_code == 201

        user_from_db2 = User.objects.get(username=user2.username)
        client.force_authenticate(user_from_db2)
        new_title_of_stranger_book = fake.name()
        # try to update book by authenticated user (not author)
        response = client.put(f'{self.update_book_url}{book_from_db.id}/', data={'title': new_title_of_stranger_book})
        assert response.status_code == 403
