# Create your views here.
import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework import permissions
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import jwt

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .serializers import MovieSerializer, UserSerializer, UserLoginSerializer, UrlSerializer
from .models import User

SECRET_KEY = '5(@2#r4a5(4uig*hokxeq56!-9e_pz=dx660q8a%7w%8x7)ycd'


def index(request):
    return HttpResponse("Hello, world. You're at the api index.")

@csrf_exempt
def singup(request):
    data = JSONParser().parse(request)
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        encoded_jwt = create_token(email=serializer.validated_data['email'])
        serializer.save()
        return JsonResponse({"status": "success", "message": "User added suucessfully.", "token": encoded_jwt}, status=201)
    return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def login(request):
    data = JSONParser().parse(request)
    serializer = UserLoginSerializer(data=data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user_resp = is_valid_user(email=email)
        if user_resp["status"] == "error":
            return JsonResponse(user_resp, status=400)
        token = create_token(email)
        return JsonResponse({"status": "success", "message": "User login successful.", "token": token}, status=201)
    return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def fetch_data(request):
    data = JSONParser().parse(request)
    serializer = UrlSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse(serializer.errors, status=400)
    movie_info = fetch_movies_from_url(url=serializer.validated_data["url"])
    if movie_info["status"] == "error":
        return JsonResponse(movie_info, status=200)
    return JsonResponse({"status": "success", "message": "", "data": movie_info["data"]}, status=200)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-joining_date')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


def create_token(email):
    encoded_jwt = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30*60),
    }, SECRET_KEY, algorithm='HS256').decode('utf-8')
    return encoded_jwt

def is_valid_user(email):
    user = User.objects.get(email=email)
    if not user:
        return {"status": "error", "message": "unable to find user."}
    return {"status": "success", "message": "valid user."}


def fetch_movies_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    movie_table_body = soup.find('table', class_='chart full-width').find('tbody')
    all_movies_list = movie_table_body.find_all('tr')

    parsed_url = urlparse(url)
    base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

    movie_info = []
    for mov in all_movies_list:
        try:
            movie_data = {
                'rating': mov.find('td', class_='ratingColumn imdbRating').strong.text.strip(),
                'name': mov.find('td', class_='titleColumn').a.text.strip(),
                'year': mov.find('span', class_='secondaryInfo').text.strip().replace('(', '').replace(')', ''),
                'poster_url': mov.find('img')['src'].strip(),
                'movie_info_url': base_url + mov.find('a', href=True)['href'].strip()
            }
            # extra_movie_data = fetch_movie_info(relative_url=movie_data['movie_info_url'], base_url=base_url)
            # movie_data.update(extra_movie_data)
            movie_serializer = MovieSerializer(data=movie_data)
            if not movie_serializer.is_valid():
                continue
                # return {"status": "error", "errors": movie_serializer.errors, "message": ""}
            
            movie_serializer.save()
            movie_info.append(movie_data)
        except Exception as e:
            print(e)
            continue
    
    if len(movie_info) == 0:
        return {"status": "error", "message": "No movie to add."}
    return {"status": "success", "data": movie_info}


def fetch_movie_info(relative_url, base_url):
    url = base_url + relative_url

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    plot_sum_wrap = soup.find('div', class_='plot_summary_wrapper').find('div', class_='plot_summary')
    sum_text = plot_sum_wrap.find('div', class_='summary_text').text.strip()

    credit_items = plot_sum_wrap.find_all('div', class_='credit_summary_item')
    credit_items = {i.h4.text.replace(':', ''): i.a.text for i in credit_items}

    title_wrapper = soup.find('div', class_='title_wrapper')
    movie_duration = title_wrapper.find('div', class_='subtext').time.text.strip()
    other_info = title_wrapper.find('div', class_='subtext').find_all('a', href=True)
    other_info = [y.text.strip() for y in other_info]

    return {
        'summary_text': sum_text,
        'credits': credit_items,
        'movie_duration': movie_duration,
        'extra_info': other_info
    }
