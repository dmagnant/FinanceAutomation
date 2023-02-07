from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.scripts, name="scripts"),
    path('ally', views.ally, name="Ally"),
    path('amazon', views.amazon, name="AmazonGC"),
    path('amex', views.amex, name="Amex"),
    path('barclays', views.barclays , name="Barclays"),
    path('bing', views.bing, name="Bing"),
    path('boa', views.boa , name="BoA"),
    path('chase', views.chase, name="Chase"),
    path('coinbase', views.coinbase, name="Coinbase"),
    path('dailyBank', views.dailyBank, name="Daily_Bank"),
    path('dailyMR', views.dailyMR, name="Daily_MR"),  
    path('discover', views.discover, name="Discover"),
    path('eternl', views.eternl, name="Eternl"),
    path('exodus', views.exodus, name="Exodus"),
    path('fidelity', views.fidelity, name="Fidelity"),
    path('healthEquity', views.healthEquity , name="HealthEquity"),
    path('ioPay', views.ioPay, name="IoPay"),
    path('kraken', views.kraken, name="Kraken"),
    path('ledger', views.ledger, name="Ledger"),
    path('monthlyBank', views.monthlyBank , name="Monthly_Bank"),
    path('myConstant', views.myConstant , name="MyConstant"),
    path('paidviewpoint', views.paidviewpoint, name="Paidviewpoint"),
    path('paypal', views.paypal, name="Paypal"),
    path('pinecone', views.pinecone, name="Pinecone"),
    path('presearch', views.presearch, name="Presearch"),
    path('pscoupons', views.psCoupons, name="PSCoupons"),
    path('sofi', views.sofi, name="Sofi"),
    path('swagbucks', views.swagbucks, name="Swagbucks"),
    path('tellwut', views.tellwut, name="Tellwut"),
    path('updateGoals', views.updateGoals , name="UpdateGoals"),
    path('vanguard', views.vanguard , name="Vanguard"),
    path('worthy', views.worthy , name="Worthy")
]