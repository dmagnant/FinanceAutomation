import os
import os.path

from django.shortcuts import render

from scripts.scripts.Ally import *
from scripts.scripts.AmazonGC import *
from scripts.scripts.Amex import *
from scripts.scripts.Barclays import *
from scripts.scripts.Bing import *
from scripts.scripts.BoA import *
from scripts.scripts.Chase import *
from scripts.scripts.Cointiply import *
from scripts.scripts.Daily_Bank import *
from scripts.scripts.Daily_MR import *
from scripts.scripts.Discover import *
from scripts.scripts.Functions.WebDriverFunctions import openWebDriver
from scripts.scripts.Pinecone import *
from scripts.scripts.Presearch import *
from scripts.scripts.Sofi import *
from scripts.scripts.Swagbucks import *
from scripts.scripts.Tellwut import *

def scripts(request):
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts')
    scripts.sort()
    try:
        scripts.remove("Functions")
        scripts.remove("Cointiply.py")
        scripts.remove("__pycache__")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        i = scripts.index(script)
        script = script.replace('.py','')
        scripts[i] = script
    return render(request,"scripts/scripts.html", {'scripts':scripts})

def amex(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runAmex(driver)
        elif "login" in request.POST:
            amexLogin(driver)
        elif "balance" in request.POST:
            balance = getAmexBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimAmexRewards(driver)
    return render(request,"scripts/amex.html")

def barclays(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runBarclays(driver)
        elif "login" in request.POST:
            barclaysLogin(driver)
        elif "balance" in request.POST:
            balance = getBarclaysBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimBarclaysRewards(driver)
    return render(request,"scripts/barclays.html")

def boa(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main_P" in request.POST:
            runAmex(driver, "p")
        elif "main_J" in request.POST:
            runAmex(driver, "j")
        elif "login" in request.POST:
            boALogin(driver)
        elif "balance_P" in request.POST:
            balance = getBoABalance(driver, "p")
            print(balance)
        elif "balance_J" in request.POST:
            balance = getBoABalance(driver, "j")
            print(balance)            
        elif "rewards_P" in request.POST:
            claimBoARewards(driver, "p")
        elif "rewards_J" in request.POST:
            claimBoARewards(driver, "J")            
    return render(request,"scripts/boa.html")

def chase(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runChase(driver)
        elif "login" in request.POST:
            chaseLogin(driver)
        elif "balance" in request.POST:
            balance = getChaseBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimChaseRewards(driver)    
    return render(request,"scripts/chase.html")

def discover(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            runDiscover(driver)
        elif "login" in request.POST:
            discoverLogin(driver)
        elif "balance" in request.POST:
            balance = getDiscoverBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimDiscoverRewards(driver)    
    return render(request,"scripts/discover.html")

def ally(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            allyBalanceAndTransactions = runAlly(driver)
            print(allyBalanceAndTransactions)
        elif "login" in request.POST:
            allyLogin(driver)
        elif "balance" in request.POST:
            balance = getAllyBalance(driver)
            print(balance)
    return render(request,"scripts/ally.html")

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

def dailyBank(request):
    if "main" in request.POST:
        runDailyBank()
    return render(request,"scripts/dailyBank.html")

def dailyMR(request):
    if "main" in request.POST:
        runDailyMR()
    return render(request,"scripts/dailyMR.html")

def paypal(request):
    if "main" in request.POST:
        runPaypal()
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
            balance = getPineConeBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimPineConeRewards(driver) 
    return render(request,"scripts/pinecone.html")

def presearch(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        directory = setDirectory()
        if "redeemRewards" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(directory, driver)
        elif "login" in request.POST:
            presearchLogin(driver)            
        elif "balance" in request.POST:
            print(getPresearchBalance(driver)[0])
        elif "search" in request.POST:
            searchUsingPresearch(driver)       
    return render(request,"scripts/presearch.html")

def sofi(request):
    if request.method == 'POST':
        driver = openWebDriver("Chrome")
        driver.implicitly_wait(5)
        if "main" in request.POST:
            sofiBalanceAndTransactions = runSofi(driver)
            print(sofiBalanceAndTransactions)
        elif "login" in request.POST:
            sofiLogin(driver)
        elif "checkingBalance" in request.POST:
            balance = getSofiBalanceAndOrientPage(driver, "Checking")[0]
            print('checking balance: ', balance)
        elif "savingsBalance" in request.POST:
            balance = getSofiBalanceAndOrientPage(driver, "Savings")[0]
            print('savings balance: ', balance)
    return render(request,"scripts/sofi.html")

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
            balance = getSwagBucksBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimSwagBucksRewards(driver)
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
    return render(request,"scripts/crypto.html",)
