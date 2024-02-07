import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from faker import Faker
from app.models import User


class TestUser:
    email = 'alex@authors.com'
    fake = Faker()

    @pytest.mark.django_db
    def test_create_user(self, user_factory):
        user = user_factory.build(email=self.email)
        user.clean_fields()
        user.save()

        assert User.objects.count() == 1

    @pytest.mark.django_db
    def test_invalid_email_create_user(self, user_factory):
        with pytest.raises(ValidationError) as exc:
            user = user_factory.build(email=self.email.split('.')[0])
            user.clean_fields()
            user.save()

        assert not User.objects.all().exists()
        assert 'email' in exc.value.error_dict

    @pytest.mark.django_db
    def test_correct_age_create_user(self, user_factory):
        user_factory.create(age=10, email=self.email).clean_fields()

        assert User.objects.filter(age=10).exists()

    @pytest.mark.django_db
    def test_string_age_create_user(self, user_factory):
        with pytest.raises(ValidationError) as exc:
            user = user_factory.build(age='ten', email=self.email)
            user.clean_fields()
            user.save()
        assert 'age' in exc.value.error_dict

    @pytest.mark.django_db
    def test_invalid_age_create_user(self, user_factory):
        with pytest.raises(ValidationError) as exc:
            user = user_factory.build(age=9, email=self.email)
            user.clean_fields()
            user.save()
        assert 'age' in exc.value.error_dict
        assert not User.objects.filter(age=9).exists()

    @pytest.mark.django_db
    def test_empty_email_create_user(self, user_factory):
        with pytest.raises(ValidationError) as exc:
            user = user_factory.build()
            user.clean_fields()
            user.save()
        assert 'email' in exc.value.error_dict

    @pytest.mark.django_db
    def test_email_none_create_user(self, user_factory):
        with pytest.raises(IntegrityError) as exc:
            user = user_factory.build(email=None)
            user.clean_fields()
            user.save()
        assert 'email' in str(exc)

    @pytest.mark.django_db
    def test_duplicate_create_user(self, user_factory):
        with pytest.raises(IntegrityError) as exc:
            user_factory(email=self.email)
            user_factory(email=self.email)
        assert 'unique constraint' in str(exc)

    @pytest.mark.django_db
    def test_success_two_unique_create_user(self, user_factory):
        for i in range(10):
            username = self.fake.name()
            email = f'{username}@{self.email.split("@")[-1]}'
            user_factory(username=username, email=email)
        assert User.objects.all().count() == 10
