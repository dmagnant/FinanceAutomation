from django.shortcuts import render

import sys
sys.path.append("..")
from scripts.scripts.Functions import openWebDriver, showMessage
from scripts.scripts.MarketResearch.Swagbucks import contentDiscovery

# Create your views here.
def accounts(request):
    return render(request,"accounts/accounts.html")

def swagbucks(request):
    driver = openWebDriver("Chrome")
    print(request)
    if request.method == 'POST' and "login" in request.POST:
        contentDiscovery(driver)
    return render(request,"accounts/swagbucks.html")