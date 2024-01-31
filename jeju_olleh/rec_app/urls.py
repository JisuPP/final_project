from django.contrib import admin
from django.urls import path, include
from . import views  # views.py에서 필요한 함수들을 불러옵니다.

app_name = 'rec_app'

urlpatterns = [
    path('', views.rec_input, name='rec_input'),
    path('detail/<str:destination>/', views.detail, name='detail'),
    path('about/', views.about, name='about'),
    path('place_rec/',views.place_rec, name='place_rec' ),
    path('rec_place/',views.rec_place, name='rec_place' ),
    path('map/',views.map, name='map' ),
]
