from django.urls import include, path
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("index", views.index, name="index"),
    path("movie", views.fetch_data, name="movie_post"),
    path("fetch_movies", views.fetch_movies, name="fetch_movie"),
    path(
        "movie_by_name/<str:name>",
        views.fetch_movie_by_name,
        name="fetch_movie_by_name",
    ),
    path("update_movie_list", views.update_movie_list, name="update_movie_list"),
    path("get_movie_list/<str:list_name>", views.get_movie_list, name="get_movie_list"),
    path("user_signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
