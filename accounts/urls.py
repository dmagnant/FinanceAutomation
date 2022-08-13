from django.urls import path, include

from . import views

urlpatterns = [
    path('swagbucks', views.swagbucks, name="swagbucks"),
]