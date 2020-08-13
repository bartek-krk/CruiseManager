from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^weather/$', views.weather, name='weather'),
    url(r'^songs/$', views.songs, name='songs'),
    url(r'^map/$', views.map, name='map'),
]