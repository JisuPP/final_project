"""final_projcet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jeju_app.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


### url 패턴을 변경해준다. -> 우리가 사용하려는 app 의 명을 따와서 변경해준다.
# ### travel_predict 로 변경? 이런식으로 해야함
# urlpatterns = [
#     path('', include('index.urls')), # http://localhost:8000 으로 클라이언트가 서버에 요청했을 경우 -> home 화면
#     path('about/', include("about.urls")), # http://localhost:8000/'앱이름' 으로 클라이언트가 서버에 요청했을 경우
#     path('others/', include("others.urls")) # http://localhost:8000/'앱이름' 으로 클라이언트가 서버에 요청했을 경우
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)