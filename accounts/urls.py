from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.accounts, name="accounts"),
    path('amazon', views.amazon, name="AmazonGC"),
    path('bing', views.bing, name="Bing"),
    path('cointiply', views.cointiply, name="Cointiply"),
    path('pinecone', views.pinecone, name="Pinecone"),
    path('presearch', views.presearch, name="Presearch_MR"),
    path('swagbucks', views.swagbucks, name="Swagbucks"),
    path('tellwut', views.tellwut, name="Tellwut")
]