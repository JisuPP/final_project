from django.urls import path
from . import views
# url을 변수로 사용하기 => app_name:name
app_name = 'review_app'
urlpatterns = [
    path('create/<str:title>/', views.create, name='create'),
    path('index/<str:title>/', views.index, name='index'),
    path('<str:title>/<int:pk>/', views.detail, name='detail'),
]