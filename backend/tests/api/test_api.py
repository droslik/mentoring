import pytest
from django.urls import reverse
from faker import Faker
from requests import Response
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.mark.django_db
class TestBook:
    fake = Faker()
    client = APIClient()
    create_user_url = '/api/v1/users/create_user/'
    own_user_url = '/api/v1/users/own/'
    create_book_url = '/api/v1/books/create_book/'
    update_book_url = '/api/v1/books/{pk}/'

    def test_url(self):
        assert self.create_user_url == reverse('create-user')
        assert self.own_user_url == reverse('own')
        assert self.create_book_url == reverse('create-book')

    def test_register_user(self, user_factory):
        user_factory.build()
        data = {
            'username': user_factory.username,
            'email': user_factory.email,
            'password': user_factory.password,
        }
        response = self.client.post(reverse('create-user'), data)
        assert response.status_code == 201

    def test_username_exists_register_user(self, user_factory):
        user_factory()
        data = {
            'username': user_factory.username,
            'email': user_factory.email,
            'password': user_factory.password,
        }
        response = self.client.post(reverse('create-user'), data)

        assert 'username already exists' in str(response.json()['username'])

    def test_without_username_register_user(self, user_factory):
        data = {
            'email': user_factory.email,
            'password': user_factory.password,
        }
        response = self.client.post(reverse('create-user'), data)
        assert 'username' in response.json().keys()
        assert 'This field is required' in str(response.json())

    def test_without_password_register_user(self, user_factory):
        data = {
            'username': user_factory.username,
            'email': user_factory.email,
        }
        response = self.client.post(reverse('create-user'), data)

        assert 'password' in response.json().keys()

    def test_incorrect_email_register_user(self, user_factory):
        data = {
            'username': user_factory.username,
            'email': '123',
            'password': user_factory.password,
        }
        response = self.client.post(reverse('create-user'), data)
        assert 'email' in response.json().keys()
        assert 'Enter a valid email address' in str(response.json())

    def test_own_user_page(self, user_factory):
        user = user_factory()
        self.client.force_login(user)
        response = self.client.get(reverse('own'))

        assert response.status_code == 200

    def test_own_user_401_error_code(self, user_factory):
        user_factory()
        response = self.client.get(reverse('own'))

        assert response.status_code == 401

    @patch('requests.get')
    def test_create_book_201(self, mock_requests, user_factory, book_factory):
        book = book_factory.build(author=user_factory())
        response = Response()
        response.status_code = 200
        mock_requests.return_value = response
        self.client.force_login(book.author)
        book_data = {
            'title': book.title,
            'author': book.author.pk,
            'short_description': book.short_description,
        }
        response = self.client.post(reverse('create-book'), book_data)
        assert response.status_code == 201

    @patch('requests.get')
    def test_create_book_400_without_title(self, mock_requests, user_factory, book_factory):
        book = book_factory.build(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 200
        mock_requests.return_value = inner_response
        self.client.force_login(book.author)
        book_data = {
            'author': book.author,
            'short_description': book.short_description,
        }
        response_json = self.client.post(reverse('create-book'), book_data).json()

        assert 'title' in response_json.keys() and 'This field is required' in str(response_json)

    def test_create_book_403_error_code(self, user_factory, book_factory):
        book = book_factory.build(author=user_factory())
        book_data = {
            'title': book.title,
            'author': book.author.id,
            'short_description': book.short_description,
        }
        self.client.logout()
        response = self.client.post(reverse('create-book'), book_data)

        assert response.status_code == 403

    @patch('requests.get')
    def test_create_book_incorrect_inner_url(self, mock_requests, user_factory, book_factory):
        book = book_factory.build(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 400
        mock_requests.return_value = inner_response
        self.client.force_login(book.author)
        book_data = {
            'title': book.title,
            'author': book.author.id,
            'short_description': book.short_description,
        }
        response = self.client.post(reverse('create-book'), book_data)

        assert response.status_code == 400

    @patch('requests.get')
    def test_create_book_incorrect_2_inner_url(self, mock_requests, user_factory, book_factory):
        book = book_factory.build(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 404
        mock_requests.return_value = inner_response
        self.client.force_login(book.author)
        book_data = {
            'title': book.title,
            'author': book.author,
            'short_description': book.short_description,
        }
        response = self.client.post(reverse('create-book'), book_data)

        assert response.status_code == 400

    @patch('requests.get')
    def test_update_book_by_author(self,  mock_requests, user_factory, book_factory):
        book = book_factory(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 200
        mock_requests.return_value = inner_response
        self.client.force_login(book.author)
        new_book_data = {
            'title': self.fake.name(),
        }
        response = self.client.patch(self.update_book_url.format(pk=book.id), data=new_book_data)
        book.refresh_from_db()
        assert response.status_code == 200
        assert book.title == new_book_data['title']

    @patch('requests.get')
    def test_update_book_by_unauthenticated_user(self, mock_requests, user_factory, book_factory):
        book = book_factory(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 200
        mock_requests.return_value = inner_response
        new_book_data = {
            'title': self.fake.name(),
        }
        self.client.logout()
        response = self.client.patch(self.update_book_url.format(pk=book.id), data=new_book_data)
        assert response.status_code == 401

    @patch('requests.get')
    def test_update_book_by_not_author(self, mock_requests, user_factory, book_factory):
        book = book_factory(author=user_factory())
        inner_response = Response()
        inner_response.status_code = 200
        self.client.force_login(user_factory(username='alex2'))
        mock_requests.return_value = inner_response
        new_book_data = {
            'title': self.fake.name(),
        }
        response = self.client.patch(self.update_book_url.format(pk=book.id), data=new_book_data)
        assert response.status_code == 403
