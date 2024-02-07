from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.


class User(AbstractUser):
    age = models.IntegerField(validators=[MinValueValidator(10), MaxValueValidator(100)], blank=True, null=True)

    def __str__(self):
        return f'{self.username}'


class Book(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name='books')
    short_description = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'
