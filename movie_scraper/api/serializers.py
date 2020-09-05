from requests.api import request
from rest_framework import serializers

from .models import User, Movie, UserMovies


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "joining_date"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=256)


class UrlSerializer(serializers.Serializer):
    url = serializers.CharField(required=True, max_length=256)


class MovieListSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    list_name = serializers.CharField(required=True, max_length=30)


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movie
        fields = ["name", "year", "rating", "poster_url", "movie_info_url"]


class UserMovieSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = UserMovies
        fields = ["list_type", "movies"]


class PermissionSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=256)
    permission_name = serializers.CharField(required=True, max_length=30)


class AdminUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=200)
    email = serializers.CharField(required=True, max_length=256)
    code = serializers.CharField(required=True, max_length=30)
