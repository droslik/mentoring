from rest_framework import serializers

from app.models import User, Book


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating of users
    """

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'age',
        )

        extra_kwargs = {
            'username': {'write_only': True},
            'password': {'write_only': True},
            'email': {'write_only': True},
            'first_name': {'write_only': True},
            'last_name': {'write_only': True},
            'age': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class BookSerializer(serializers.ModelSerializer):
    author = serializers.CurrentUserDefault()

    class Meta:
        model = Book
        fields = (
            'title',
            'short_description',
            'author',
        )


class UserSerializer(serializers.ModelSerializer):
    books = serializers.ListSerializer(child=BookSerializer())

    class Meta:
        model = User
        exclude = (
            'password',
        )
