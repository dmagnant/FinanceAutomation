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
from scripts.scripts.Coinbase import *
from scripts.scripts.Cointiply import *
from scripts.scripts.Daily_Bank import *
from scripts.scripts.Daily_MR import *
from scripts.scripts.Discover import *
from scripts.scripts.Eternl import *
from scripts.scripts.Exodus import *
from scripts.scripts.HealthEquity import *
from scripts.scripts.IoPay import *
from scripts.scripts.Kraken import *
from scripts.scripts.Midas import *
from scripts.scripts.Monthly_Bank import *
from scripts.scripts.MyConstant import *
from scripts.scripts.Paypal import *
from scripts.scripts.Pinecone import *
from scripts.scripts.Presearch import *
from scripts.scripts.Sofi import *
from scripts.scripts.Swagbucks import *
from scripts.scripts.Tellwut import *
from scripts.scripts.UpdateGoals import *
from scripts.scripts.Vanguard import *
from scripts.scripts.Worthy import *
from scripts.scripts.Classes.WebDriver import Driver

def scripts(request):
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts')
    scripts.sort()
    try:
        scripts.remove("Functions")
        scripts.remove("Cointiply.py")
        scripts.remove("__pycache__")
        scripts.remove("Classes")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        i = scripts.index(script)
        script = script.replace('.py','')
        scripts[i] = script
    return render(request,"scripts/scripts.html", {'scripts':scripts})

def ally(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runAlly(driver)
            response.getData()
        elif "login" in request.POST:
            locateAllyWindow(driver)
        elif "balance" in request.POST:
            balance = getAllyBalance(driver)
            print(balance)
    return render(request,"scripts/ally.html")

def amazon(request):
    balance = ""
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            balance = confirmAmazonGCBalance(driver)
    return render(request,"scripts/amazon.html", {'balance':balance})

def amex(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runAmex(driver)
        elif "login" in request.POST:
            locateAmexWindow(driver)
        elif "balance" in request.POST:
            balance = getAmexBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimAmexRewards(driver)
    return render(request,"scripts/amex.html")

def barclays(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runBarclays(driver)
        elif "login" in request.POST:
            locateBarclaysWindow(driver)
        elif "balance" in request.POST:
            balance = getBarclaysBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimBarclaysRewards(driver)
    return render(request,"scripts/barclays.html")

def bing(request):
    if request.method == 'POST':
        driver = Driver("Edge", False)
        if "main" in request.POST:
            runBing(driver.webDriver)
        elif "login" in request.POST:
            bingLogin(driver.webDriver)
        elif "activities" in request.POST:
            bingActivities(driver.webDriver)
        elif "balance" in request.POST:
            getBingBalance(driver.webDriver)
        elif "rewards" in request.POST:
            claimBingRewards(driver.webDriver)
    return render(request,"scripts/bing.html")

def boa(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        account = body.get("account")
        if "main" in request.POST:
            runBoA(driver, account)
        elif "login" in request.POST:
            locateBoAWindowAndOpenAccount(driver, account)
        elif "balance" in request.POST:
            balance = getBoABalance(driver, account)
            print(balance)          
        elif "rewards" in request.POST:
            claimBoARewards(driver, account)
    return render(request,"scripts/boa.html")

def chase(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runChase(driver)
        elif "login" in request.POST:
            locateChaseWindow(driver)
        elif "balance" in request.POST:
            balance = getChaseBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimChaseRewards(driver)    
    return render(request,"scripts/chase.html")

def coinbase(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            main = "method"
    return render(request,"scripts/coinbase.html")

def dailyBank(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runDailyBank()
        elif "prices" in request.POST:
            updateCryptoPrices(driver)
    return render(request,"scripts/dailyBank.html")

def dailyMR(request):
    if "main" in request.POST:
        runDailyMR()
    return render(request,"scripts/dailyMR.html")

def discover(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runDiscover(driver)
        elif "login" in request.POST:
            locateDiscoverWindow(driver)
        elif "balance" in request.POST:
            balance = getDiscoverBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimDiscoverRewards(driver)    
    return render(request,"scripts/discover.html")

def eternl(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runEternl(driver.webDriver)
            for coin in response:
                coin.getData()
        elif "balance" in request.POST:
            response = getEternlBalance(driver.webDriver)
            print(response)
        elif "login" in request.POST:
            locateEternlWindow(driver)
    return render(request,"scripts/eternl.html")

def exodus(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runExodus()
            for coin in response:
                coin.getData()
    return render(request,"scripts/exodus.html")

def healthEquity(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST or "balance" in request.POST:
            today = datetime.today()
            year = today.year
            month = today.month
            lastMonth = getStartAndEndOfDateRange(today, month, year, "month")
            response = getHealthEquityBalances(driver, lastMonth)
            print('HSA balance: ' + str(response[0]))
            print('401k balance: ' + str(response[2]))
        elif "login" in request.POST:
            locateHealthEquityWindow(driver)
    return render(request,"scripts/healthEquity.html")

def ioPay(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runIoPay()
            print('balance: ' + str(response))
    return render(request,"scripts/iopay.html")

def kraken(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runKraken(driver)
            for coin in response:
                coin.getData()
        elif "balance" in request.POST:
            response = getKrakenBalances(driver)
            print(response)
        elif "login" in request.POST:
            locateKrakenWindow(driver)
    return render(request,"scripts/kraken.html")

def midas(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST or "balance" in request.POST:
            response = runMidas(driver) if "main" in request.POST else getMidasBalances(driver)
            for coin in response:
                coin.getData()
        elif "login" in request.POST:
            locateMidasWindow(driver)
    return render(request,"scripts/midas.html")

def monthlyBank(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        if "main" in request.POST:
            currency = body.get("type")
            today = datetime.today()
            if currency == "USD":
                usdbalances = runUSD(driver, today)
                print(f'MyConstant: {usdbalances[0]} \n' 
                f'Worthy: {usdbalances[1]} \n' 
                f'Liquid Assets: {usdbalances[2]} \n' 
                f'401k: {usdbalances[3]} \n'
                f'NM HSA: {usdbalances[4]} \n')
            elif currency == "Crypto":
                cryptoBalance = runCrypto(driver, today)
                print('Crypto Balance: ' + str(cryptoBalance))
            elif currency == "Both":
                runMonthlyBank()
    return render(request,"scripts/monthlyBank.html")

def myConstant(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        if "main" in request.POST or "balance" in request.POST:
            currency = body.get("type")
            response = runMyConstant(driver, currency) if "main" in request.POST else getMyConstantBalances(driver, currency)
            if currency == "USD":
                response.getData()
            elif currency == "Crypto":
                for coin in response:
                    coin.getData()
        elif "login" in request.POST:
            locateMyConstantWindow(driver)
    return render(request,"scripts/myconstant.html")

def paypal(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
    if "main" in request.POST:
        runPaypal(driver)
    elif "login" in request.POST:
        locatePayPalWindow(driver)
    return render(request,"scripts/paypal.html")

def pinecone(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPinecone(driver)
        elif "login" in request.POST:
            locatePineconeWindow(driver)
        elif "balance" in request.POST:
            balance = getPineConeBalance(driver)
            print(balance)
        elif "rewards" in request.POST:
            claimPineConeRewards(driver) 
    return render(request,"scripts/pinecone.html")

def presearch(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "rewards" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(driver)
        elif "login" in request.POST:
            locatePresearchWindow(driver)          
        elif "balance" in request.POST:
            balance = getPresearchBalance(driver)
            print(balance[0])
        elif "search" in request.POST:
            searchUsingPresearch(driver)
    return render(request,"scripts/presearch.html")

def sofi(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            response = runSofi(driver)
            for accounts in response:
                accounts.getData()
        elif "login" in request.POST:
            locateSofiWindow(driver)
        elif "checkingBalance" in request.POST:
            balance = getSofiBalanceAndOrientPage(driver, "Checking")[0]
            print('checking balance: ', balance)
        elif "savingsBalance" in request.POST:
            balance = getSofiBalanceAndOrientPage(driver, "Savings")[0]
            print('savings balance: ', balance)
    return render(request,"scripts/sofi.html")

def swagbucks(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runSwagbucks(driver, True) if "Run Alu" in request.POST else runSwagbucks(driver, False)
        elif "login" in request.POST:
            locateSwagBucksWindow(driver)
        elif "alu" in request.POST:
            runAlusRevenge(driver.webDriver, True)
        elif "content" in request.POST:
            swagBuckscontentDiscovery(driver.webDriver)
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
        driver = Driver("Chrome")
        if "main" in request.POST:
            runTellwut(driver)
        elif "login" in request.POST:
            locateTellWutWindow(driver)
        elif "surveys" in request.POST:
            completeTellWutSurveys(driver)            
        elif "balance" in request.POST:
            getTellWutBalance(driver)
        elif "rewards" in request.POST:
            redeemTellWutRewards(driver)
    return render(request,"scripts/tellwut.html")

def updateGoals(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()        
        if "main" in request.POST:
            account = body.get("accounts")
            timeframe = body.get("TimeFrame")
            runUpdateGoals(account, timeframe)
    return render(request,"scripts/updateGoals.html")

def vanguard(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runVanguard(driver)
        elif "login" in request.POST:
            locateVanguardWindow(driver)
        elif "balance" in request.POST:
            balance = getVanguardBalanceAndInterestYTD(driver)
            print(balance[0])
    return render(request,"scripts/vanguard.html")

def worthy(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST or "balance" in request.POST:
            response = getWorthyBalance(driver)
            print(f'total balance: {response}')
        elif "login" in request.POST:
            locateWorthyWindow(driver)
    return render(request,"scripts/worthy.html")

def marketResearch(request):
    return render(request,"scripts/marketresearch.html")

def usd(request):
    return render(request,"scripts/usd.html")

def crypto(request):
    return render(request,"scripts/crypto.html",)
