from django.urls import path, include

from . import views

urlpatterns = [
    path('usd', views.usd, name="usd"),
    path('crypto', views.crypto, name="crypto"),
    path('marketresearch', views.marketResearch, name="marketresearch"),
]