# Generated by Django 4.1 on 2024-01-27 20:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='age',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
