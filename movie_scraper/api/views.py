from django.http import HttpResponse, JsonResponse

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Movie
from .serializers import (
    MovieSerializer,
    UserSerializer,
    UserLoginSerializer,
    UrlSerializer,
)
from .utils import (
    create_token,
    decode_token,
    is_admin,
    is_valid_user,
    fetch_movies_from_url,
)


def index(request):
    return HttpResponse("Hello, world. You're at the api index.")


@api_view(["POST"])
def signup(request):
    data = JSONParser().parse(request)
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        encoded_jwt = create_token(email=serializer.validated_data["email"])
        serializer.save()
        return JsonResponse(
            {
                "status": "success",
                "message": "User added suucessfully.",
                "token": encoded_jwt,
            },
            status=201,
        )
    return JsonResponse(serializer.errors, status=400)


@api_view(["POST"])
def login(request):
    data = JSONParser().parse(request)
    serializer = UserLoginSerializer(data=data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user_resp = is_valid_user(email=email)
        if user_resp["status"] == "error":
            return JsonResponse(user_resp, status=400)
        token = create_token(email)
        return JsonResponse(
            {"status": "success", "message": "User login successful.", "token": token},
            status=201,
        )
    return JsonResponse(serializer.errors, status=400)


@api_view(["POST"])
def fetch_data(request):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=402)

    if not is_admin(user=token_resp["user"]):
        return Response(
            {"status": "error", "message": "Permission denied."}, status=412
        )

    data = JSONParser().parse(request)
    serializer = UrlSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    movie_info = fetch_movies_from_url(url=serializer.validated_data["url"])
    if movie_info["status"] == "error":
        return JsonResponse(movie_info, status=200)
    return JsonResponse(
        {"status": "success", "message": "", "data": movie_info["data"]}, status=200
    )


@api_view(["GET"])
def fetch_movies(request):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=402)

    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
def fetch_movie_by_name(request, name):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=402)

    try:
        movie = Movie.objects.get(name=name)
    except Movie.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MovieSerializer(movie)
    return Response(serializer.data)
