from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('index', views.index, name='index'),
    path('movie', views.fetch_data, name='movie_post'),
    path('user_signup', views.singup, name='signup'),
    path('login', views.login, name='login'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]