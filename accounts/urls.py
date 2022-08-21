from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.accounts, name="accounts"),
    path('swagbucks', views.swagbucks, name="swagbucks"),
]