from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'rec_app'

urlpatterns = [
    path('', views.recommendation_input, name='recommendation_input'),
]
