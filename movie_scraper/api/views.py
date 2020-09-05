from django.http import HttpResponse, JsonResponse

from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .constants import ADMIN_TOKEN, VALID_MOVIE_LISTS, VALID_PERMISSIONS
from .models import Movie, UserMovies, UserPermissions
from .serializers import (
    AdminUserSerializer,
    MovieListSerializer,
    MovieSerializer,
    PermissionSerializer,
    UserSerializer,
    UserLoginSerializer,
    UrlSerializer,
)
from .utils import (
    create_token,
    decode_token,
    fetch_movie_info,
    has_permission,
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
    return JsonResponse(
        {
            "status": "error",
            "message": "Error while creating login token",
            "errors": serializer.errors,
        },
        status=400,
    )


@api_view(["POST"])
def fetch_data(request):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=403)

    if not has_permission(user=token_resp["user"], permission_required="fetch_movies"):
        return Response(
            {"status": "error", "message": "Permission denied."}, status=403
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
        return Response(token_resp, status=403)

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
        return Response(token_resp, status=403)

    try:
        movie = Movie.objects.get(name__icontains=name.strip())
    except Movie.DoesNotExist:
        return Response(
            {"status": "error", "message": "Unable to find movie"}, status=400
        )

    serializer = MovieSerializer(movie)
    data = serializer.data

    extra_info = fetch_movie_info(data["movie_info_url"])
    data["extra_info"] = extra_info

    return Response(
        {
            "status": "success",
            "message": "Movie info fetched successfully",
            "data": data,
        },
        status=200,
    )


@api_view(["POST", "DELETE"])
def update_movie_list(request):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=403)

    data = JSONParser().parse(request)
    serializer = MovieListSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": "", "errors": serializer.errors}, status=400
        )

    list_name = serializer.validated_data["list_name"]
    if list_name not in VALID_MOVIE_LISTS:
        return Response(
            {"status": "error", "message": "Invalid list type."}, status=400
        )

    try:
        movie = Movie.objects.get(name=serializer.validated_data["name"])
    except Movie.DoesNotExist:
        return Response(
            {"status": "error", "message": "Unable to locate movie."}, status=400
        )

    user = token_resp["user"]
    already_present = False
    try:
        user_movie = UserMovies.objects.get(user=user, movie=movie)
        already_present = True
    except UserMovies.DoesNotExist:
        user_movie = None

    if request.method == "POST":
        if already_present:
            return Response(
                {"status": "error", "message": "Movie is already added to the list."},
                status=200,
            )

        user_movie_list = UserMovies(
            user=token_resp["user"], movie=movie, list_type=list_name
        )
        user_movie_list.save()

        return Response(
            {"status": "success", "message": f"{list_name.title()} updated."},
            status=201,
        )

    elif request.method == "DELETE":
        if not already_present:
            return Response(
                {"status": "error", "message": "Movie is not present in the list."},
                status=200,
            )

        user_movie.delete()
        return Response(
            {
                "status": "success",
                "message": f"{user_movie.movie.name} is successfully removed from {list_name}.",
            },
            status=200,
        )


@api_view(["GET"])
def get_movie_list(request, list_name):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=403)

    if list_name not in VALID_MOVIE_LISTS:
        return Response(
            {"status": "error", "message": "Invalid list type."}, status=400
        )

    data = {
        "movies": [],
        "list_name": list_name,
        "user_name": token_resp["user"].name,
        "email": token_resp["user"].email,
    }
    try:
        user_movies = UserMovies.objects.filter(
            user_id=token_resp["user"].id, list_type=list_name
        )
    except UserMovies.DoesNotExist:
        return Response(
            {
                "status": "success",
                "message": f"No movie in the {list_name}",
                "data": data,
            },
            status=200,
        )

    for _movie in user_movies:
        movie = _movie.movie
        data["movies"].append(
            {
                "name": movie.name,
                "year": movie.year,
                "rating": movie.rating,
                "poster_url": movie.poster_url,
                "movie_info_url": movie.movie_info_url,
            }
        )

    return Response(
        {
            "status": "success",
            "message": f"{list_name.title()} fetched successfully.",
            "data": data,
        },
        status=200,
    )


@api_view(["POST", "DELETE"])
def update_user_permission(request):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=403)

    user = token_resp["user"]
    if not has_permission(user=user, permission_required="admin"):
        return Response(
            {"status": "error", "message": "Permission denied."}, status=403
        )

    data = JSONParser().parse(request)
    serializer = PermissionSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": "", "errors": serializer.errors}, status=400
        )

    permission_name = serializer.validated_data["permission_name"]
    if permission_name not in VALID_PERMISSIONS:
        return Response(
            {"status": "error", "message": "Invalid permission type."}, status=400
        )

    if not is_valid_user(serializer.validated_data["email"]):
        return Response(
            {"status": "error", "message": "Unable to find user from email provided."},
            status=400,
        )

    already_present = False
    try:
        user_permission = UserPermissions.objects.get(
            user=user, permission_name=permission_name
        )
        already_present = True
    except UserPermissions.DoesNotExist:
        user_permission = None

    if request.method == "POST":
        if already_present:
            return Response(
                {"status": "error", "message": "User already have permission."},
                status=200,
            )

        user_permission = UserPermissions(user=user, permission_name=permission_name)
        user_permission.save()

        return Response(
            {
                "status": "success",
                "message": f"{permission_name} is provided to {user.name}.",
            },
            status=201,
        )

    elif request.method == "DELETE":
        if not already_present:
            return Response(
                {"status": "error", "message": "User does not have the permission."},
                status=200,
            )

        user_permission.delete()
        return Response(
            {
                "status": "success",
                "message": f"{user_permission.permission_name} is successfully removed from {user.name}.",
            },
            status=200,
        )


@api_view(["GET"])
def get_user_permission(request, email):
    token = request.headers.get("jwt")
    if not token:
        return Response(
            {"status": "error", "message": "Auth token required."}, status=412
        )

    token_resp = decode_token(token=token)
    if token_resp["status"] == "error":
        return Response(token_resp, status=403)

    if not has_permission(user=token_resp["user"], permission_required="admin"):
        return Response(
            {"status": "error", "message": "Permission denied."}, status=403
        )

    user_resp = is_valid_user(email=email)
    if user_resp["status"] == "error":
        return Response(user_resp, status=400)

    user = user_resp["user"]
    data = {"name": user.name, "email": user.email, "permissions": []}

    user_permissions = UserPermissions.objects.filter(user=user_resp["user"])

    for permission in user_permissions:
        data["permissions"].append(permission.permission_name)

    return Response(
        {
            "status": "success",
            "message": f"Permissions fetched successfully.",
            "data": data,
        },
        status=200,
    )


@api_view(["POST"])
def create_admin_user(request):
    data = JSONParser().parse(request)
    serializer = AdminUserSerializer(data=data)
    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": "", "errors": serializer.errors}, status=400
        )

    if serializer.validated_data["code"] != ADMIN_TOKEN:
        return Response({"status": "error", "message": "Invalid token"}, status=403)

    try:
        UserPermissions.objects.get(permission_name="admin")
        return Response(
            {"status": "error", "message": "Permission Denied."}, status=403
        )
    except UserPermissions.DoesNotExist:
        pass

    user_serializer = UserSerializer(data=data)
    user_serializer.is_valid()
    user_serializer.save()  # not sure how to flush/temporarily store data in db, so directly committing.

    email = serializer.validated_data["email"]
    user_resp = is_valid_user(email=email)

    user_permission = UserPermissions(user=user_resp["user"], permission_name="admin")
    user_permission.save()

    encoded_jwt = create_token(email=serializer.validated_data["email"])
    return JsonResponse(
        {
            "status": "success",
            "message": "User added suucessfully.",
            "token": encoded_jwt,
        },
        status=201,
    )
