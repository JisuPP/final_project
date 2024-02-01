from django.contrib import admin
from django.urls import path, include
from . import views  # views.py에서 필요한 함수들을 불러옵니다.

app_name = 'rec_app'

urlpatterns = [
    # 메인 페이지
    path('', views.rec_input, name='rec_input'),

    # 서비스 관련 페이지
    path('about/', views.about, name='about'),
    path('map/',views.map, name='map' ),

    # 시스템 결과창 페이지
    path('other_rec/',views.other_rec, name='other_rec' ),
    path('rec_place/',views.rec_place, name='rec_place' ),
    path('detail/<str:destination>/', views.detail, name='detail'),
]
