from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.scripts, name="scripts"),
    # path('usd', views.usd, name="usd"),
    # path('crypto', views.crypto, name="crypto"),
    # path('marketresearch', views.marketResearch, name="marketresearch"),
    path('amazon', views.amazon, name="AmazonGC"),
    path('bing', views.bing, name="Bing"),
    path('pinecone', views.pinecone, name="Pinecone"),
    path('presearch', views.presearch, name="Presearch_MR"),
    path('swagbucks', views.swagbucks, name="Swagbucks"),
    path('tellwut', views.tellwut, name="Tellwut"),
    path('dailyMR', views.dailyMR, name="Daily_MR")
]