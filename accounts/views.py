import os
import os.path
import sys

from django.shortcuts import render

sys.path.append("..")
from scripts.scripts.Accounts.AmazonGC import *
from scripts.scripts.Accounts.Bing import *
from scripts.scripts.Accounts.Cointiply import *
from scripts.scripts.Accounts.Pinecone import *
from scripts.scripts.Accounts.Presearch_MR import *
from scripts.scripts.Accounts.Swagbucks import *
from scripts.scripts.Accounts.Tellwut import *
from scripts.scripts.Functions import openWebDriver, showMessage

# Create your views here.
def accounts(request):
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts\Accounts')
    try:
        scripts.remove("__pycache__")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        if script.endswith(".py"):
            i = scripts.index(script)
            script = script.replace('.py','')
            scripts[i] = script
        else:
            scripts.remove(script)
    return render(request,"accounts/accounts.html", {'scripts':scripts})

def amazon(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            confirmAmazonGCBalance(driver)
    return render(request,"accounts/amazon.html")

def bing(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            enter = "method here"
    return render(request,"accounts/bing.html")

def cointiply(request):
    return render(request,"accounts/cointiply.html")

def pinecone(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            enter = "method here"
    return render(request,"accounts/pinecone.html")

def presearch(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            enter = "method here"
    return render(request,"accounts/presearch.html")

def swagbucks(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runSwagbucks(driver, True) if "Run Alu" in request.POST else runSwagbucks(driver, False)
        elif "login" in request.POST:
            login(driver)
        elif "content" in request.POST:
            contentDiscovery(driver)
        elif "search" in request.POST:
            swagbucksSearch(driver)
    return render(request,"accounts/swagbucks.html")

def tellwut(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runTellwut(driver)
        elif "login" in request.POST:
            login(driver)
        elif "surveys" in request.POST:
            completeSurveys(driver)                    
        elif "rewards" in request.POST:
            redeemRewards(driver)
    return render(request,"accounts/tellwut.html")
