# Generated by Django 3.1.1 on 2020-09-04 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_movie"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movie",
            name="name",
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
