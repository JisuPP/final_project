from django.urls import path, include
from . import views

app_name = 'jeju_app'

urlpatterns = [
    # path('', views.index, name='index'),
    path('recommend/', views.recommend, name='recommend'),
    path('introduce/', views.introduce, name='introduce'),
    path('', views.recommendation_input, name='recommendation_input'),
   
] 

# urlpatterns = [
#     path('', views.home, name = 'home'), # http://localhost:8080 으로 클라이언트가 서버에 요청했을 경우 -> ai_app>views.py 에 함수 구성
#     # iris_predict 부분을 우리가 설정할 app 명으로 변경해주기
#     path('travel_predict/', views.travel_predict, name = 'travel_predict'),
# ]