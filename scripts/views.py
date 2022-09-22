from django.shortcuts import render
import os, os.path

from scripts.scripts.AmazonGC import *
from scripts.scripts.Bing import *
from scripts.scripts.Cointiply import *
from scripts.scripts.Pinecone import *
from scripts.scripts.Presearch_MR import *
from scripts.scripts.Swagbucks import *
from scripts.scripts.Tellwut import *
from scripts.scripts.Daily_MR import *
from scripts.scripts.Functions import openWebDriver, showMessage

def scripts(request):
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts')
    scripts.sort()
    try:
        scripts.remove("Functions.py")
        scripts.remove("Cointiply.py")
        scripts.remove("__pycache__")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        i = scripts.index(script)
        script = script.replace('.py','')
        scripts[i] = script
    return render(request,"scripts/scripts.html", {'scripts':scripts})

def amazon(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            confirmAmazonGCBalance(driver)       
    return render(request,"scripts/amazon.html")

def bing(request):
    if request.method == 'POST':
        driver = openWebDriver("Edge")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runBing(driver)
        elif "login" in request.POST:
            bingLogin(driver)
        elif "activities" in request.POST:
            bingActivities(driver)
        elif "balance" in request.POST:
            getBingBalance(driver)
        elif "rewards" in request.POST:
            claimBingRewards(driver)
    return render(request,"scripts/bing.html")

def dailyMR(request):
    if "main" in request.POST:
        runDailyMR()
    return render(request,"scripts/dailyMR.html")

def pinecone(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runPinecone(driver)
        elif "login" in request.POST:
            pineConeLogin(driver)
        elif "balance" in request.POST:
            getPineConeBalance(driver)
        elif "rewards" in request.POST:
            claimPineConeRewards(driver)            
    return render(request,"scripts/pinecone.html")

def presearch(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runPresearch(driver)
    return render(request,"scripts/presearch.html")

def swagbucks(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runSwagbucks(driver, True) if "Run Alu" in request.POST else runSwagbucks(driver, False)
        elif "login" in request.POST:
            swagBucksLogin(driver)
        elif "alu" in request.POST:
            runAlusRevenge(driver, True)
        elif "content" in request.POST:
            swagBuckscontentDiscovery(driver)
        elif "search" in request.POST:
            swagbucksSearch(driver)
        elif "balance" in request.POST:
            swagbucksSearch(driver)
        elif "rewards" in request.POST:
            swagbucksSearch(driver)                        
    return render(request,"scripts/swagbucks.html")

def tellwut(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runTellwut(driver)
        elif "login" in request.POST:
            tellwutLogin(driver)
        elif "surveys" in request.POST:
            completeTellWutSurveys(driver)            
        elif "balance" in request.POST:
            getTellWutBalance(driver)
        elif "rewards" in request.POST:
            redeemTellWutRewards(driver)
    return render(request,"scripts/tellwut.html")

def marketResearch(request):
    return render(request,"scripts/marketresearch.html")

def usd(request):
    return render(request,"scripts/usd.html")

def crypto(request):
    if request.method == 'POST' and "Coinbase.py" in request.POST:
        print(str(request.body)[87:].replace("='",''))
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts\Crypto')
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
    return render(request,"scripts/crypto.html",{'scripts':scripts})