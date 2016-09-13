from django.views.generic.base import RedirectView
from . import views
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^result/$', views.result, name='result'),
    url(r'^.*$', RedirectView.as_view(url='/simsum/', permanent=False), name='index'),
]