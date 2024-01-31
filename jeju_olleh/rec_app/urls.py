from django.contrib import admin
from django.urls import path, include
from . import views  # views.py에서 필요한 함수들을 불러옵니다.

app_name = 'rec_app'

urlpatterns = [
    path('', views.recommendation_input, name='recommendation_input'),
    path('detail/<str:destination>/', views.detail, name='detail'),
    path('about/', views.about, name='about'),
<<<<<<< HEAD
    path('others/', views.others, name='others'),
    path('result/', views.recommended_places, name='recommended_places'),  # 여기를 수정
=======
    path('map/',views.map, name='map' ),
>>>>>>> 5097ea2829a31a1c5cd808b6fd04946aa6fa00d5
]
