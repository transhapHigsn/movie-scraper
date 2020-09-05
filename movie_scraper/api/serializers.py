from rest_framework import serializers

from .models import User, Movie


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "joining_date"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=256)


class UrlSerializer(serializers.Serializer):
    url = serializers.CharField(required=True, max_length=256)


class MovieSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movie
        fields = ["name", "year", "rating", "poster_url", "movie_info_url"]
