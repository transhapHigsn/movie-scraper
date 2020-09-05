from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    joining_date = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=256, default="dummy@api.dev", unique=True)


class Movie(models.Model):
    name = models.CharField(max_length=200, unique=True)
    year = models.IntegerField(null=True)
    rating = models.CharField(null=True, max_length=5)
    poster_url = models.CharField(max_length=512)
    movie_info_url = models.CharField(max_length=200)
