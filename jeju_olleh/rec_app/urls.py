from django.contrib import admin
from django.urls import path, include
from . import views  # views.py에서 필요한 함수들을 불러옵니다.

app_name = 'rec_app'

urlpatterns = [
    # 메인 페이지
    path('', views.home, name='home'),
    path('rec_input/', views.rec_input, name='rec_input'),

    # 서비스 관련 페이지
    path('about/', views.about, name='about'),
    path('map/',views.map, name='map' ),
    path('rec_address/',views.rec_address, name='rec_address' ),
    # path('other_rec/',views.other_rec, name='other_rec' ),

    # 시스템 결과창 페이지
    path('detail/<str:destination>/', views.detail, name='detail'),

    # DB > CSV
    # path('export-django-df-to-csv/', views.export_django_df_to_csv, name='export_django_df_to_csv')

    # DB > CSV
    # path('export-to-csv/', views.export_to_csv, name='export_to_csv'),

]