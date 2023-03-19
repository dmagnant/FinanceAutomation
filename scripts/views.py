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
from scripts.scripts.Daily import *
from scripts.scripts.Discover import *
from scripts.scripts.Eternl import *
from scripts.scripts.Exodus import *
from scripts.scripts.Fidelity import *
from scripts.scripts.HealthEquity import *
from scripts.scripts.IoPay import *
from scripts.scripts.Kraken import *
from scripts.scripts.Ledger import *
from scripts.scripts.Monthly import *
from scripts.scripts.MyConstant import *
from scripts.scripts.Paypal import *
from scripts.scripts.Paidviewpoint import *
from scripts.scripts.Pinecone import *
from scripts.scripts.Presearch import *
from scripts.scripts.PSCoupons import *
from scripts.scripts.Sofi import *
from scripts.scripts.Swagbucks import *
from scripts.scripts.Tellwut import *
from scripts.scripts.UpdateGoals import *
from scripts.scripts.Vanguard import *
from scripts.scripts.Worthy import *
from scripts.scripts.Classes.WebDriver import Driver
from scripts.scripts.Classes.Asset import USD, Crypto

def scripts(request):
    bank = ['Ally', 'Sofi', 'Fidelity', 'HealthEquity', 'Vanguard', 'Worthy']
    bank.sort()
    cc = ['Amex', 'Barclays', 'BoA', 'Chase', 'Discover']
    cc.sort()
    crypto = ['Coinbase', 'Eternl', 'Exodus', 'IoPay', 'Kraken', 'Ledger', 'MyConstant', 'Presearch']
    crypto.sort()
    mr = ['AmazonGC', 'Bing', 'Paidviewpoint', 'Paypal', 'Pinecone', 'PSCoupons', 'Swagbucks', 'Tellwut']
    mr.sort()
    if "close windows" in request.POST:
        driver = Driver("Chrome")
        driver.closeWindowsExcept([':8000/'])
    context = {
        'bank':bank,
        'cc':cc,
        'crypto':crypto,
        'mr':mr}
    return render(request,"scripts/scripts.html", context)

def ally(request):
    Ally = USD("Ally")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runAlly(driver, Ally)
        elif "login" in request.POST:
            locateAllyWindow(driver)
        elif "logout" in request.POST:
            allyLogout(driver)
        elif "balance" in request.POST:
            Ally.setBalance(getAllyBalance(driver))
    context = {
        'account': Ally
    }
    return render(request,"scripts/ally.html", context)

def amazon(request):
    AmazonGC = USD("AmazonGC")    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            confirmAmazonGCBalance(driver, AmazonGC)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amazon"))
    context = {
        'AmazonGC': AmazonGC
    }
    return render(request,"scripts/amazon.html", context)

def amex(request):
    Amex = USD("Amex")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runAmex(driver, Amex)
        elif "login" in request.POST:
            locateAmexWindow(driver)
        elif "balance" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "rewards" in request.POST:
            claimAmexRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amex"))
    context = {
        'account': Amex
    }
    return render(request,"scripts/amex.html", context)

def barclays(request):
    Barclays = USD("Barclays")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runBarclays(driver, Barclays)
        elif "login" in request.POST:
            locateBarclaysWindow(driver)
        elif "balance" in request.POST:
            Barclays.setBalance(getBarclaysBalance(driver))
        elif "rewards" in request.POST:
            claimBarclaysRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
    context = {
        'account': Barclays
    }
    return render(request,"scripts/barclays.html", context)

def bing(request):
    Bing = Crypto("Bing")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runBing(driver, Bing)
        elif "login" in request.POST:
            bingLogin(driver)
        elif "activities" in request.POST:
            bingActivities(driver)
        elif "balance" in request.POST:
            Bing.setBalance(getBingBalance(driver))
            Bing.updateMRBalance(openGnuCashBook('Finance', False, False))            
        elif "rewards" in request.POST:
            claimBingRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/bing"))
    context = {
        'Bing': Bing
    }
    return render(request,"scripts/bing.html", context)

def boa(request):
    Personal = USD("BoA")
    Joint = USD("BoA-joint")
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        account = body.get("account")
        if "main" in request.POST:
            if account == 'Personal':
                runBoA(driver, Personal)
            else:
                runBoA(driver, Joint)
        elif "login" in request.POST:
                locateBoAWindowAndOpenAccount(driver, account)
        elif "balance" in request.POST:
            if account == 'Personal':
                Personal.setBalance(getBoABalance(driver, account))
            else:
                Joint.setBalance(getBoABalance(driver, account))
        elif "rewards" in request.POST:
            claimBoARewards(driver, account)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/boa"))
    context = {
        'Personal': Personal,
        'Joint': Joint       
    }
    return render(request,"scripts/boa.html", context)

def chase(request):
    Chase = USD("Chase")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runChase(driver, Chase)
        elif "login" in request.POST:
            locateChaseWindow(driver)
        elif "balance" in request.POST:
            Chase.setBalance(getChaseBalance(driver))
        elif "rewards" in request.POST:
            claimChaseRewards(driver)   
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/chase"))
    context = {
        'account': Chase
    }
    return render(request,"scripts/chase.html", context)

def coinbase(request):
    Loopring = Crypto("Loopring")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runCoinbase(driver, [Loopring])
        elif "login" in request.POST:
            locateCoinbaseWindow(driver)
        elif "balance" in request.POST:
            getCoinbaseBalances(driver, [Loopring])
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/coinbase"))            
    context = {
        'Loopring': Loopring
    }
    return render(request,"scripts/coinbase.html", context)

def creditCards(request):
    Amex = USD("Amex")
    Barclays = USD("Barclays")
    Chase = USD("Chase")
    Discover = USD("Discover")
    BoA_P = USD("BoA")
    BoA_J = USD("BoA-joint")    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "amexMain" in request.POST:
            runAmex(driver, Amex)
        elif "amexLogin" in request.POST:
            locateAmexWindow(driver)
        elif "amexBalances" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "amexRewards" in request.POST:
            claimAmexRewards(driver)
        elif "barclaysMain" in request.POST:
            runBarclays(driver, Barclays)
        elif "barclaysLogin" in request.POST:
            locateBarclaysWindow(driver)
        elif "barclaysBalances" in request.POST:
            Barclays.setBalance(getBarclaysBalance(driver))
        elif "barclaysRewards" in request.POST:
            claimBarclaysRewards(driver)
        elif "boaPMain" in request.POST:
            runBoA(driver, BoA_P)
        elif "boaPLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_P.name)
        elif "boaPBalances" in request.POST:
            BoA_P.setBalance(getBoABalance(driver, BoA_P.name))
        elif "boaPRewards" in request.POST:
            claimBoARewards(driver, BoA_P.name)
        elif "boaJMain" in request.POST:
            runBoA(driver, BoA_J)
        elif "boaJLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_J.name)
        elif "boaJBalances" in request.POST:
            BoA_J.setBalance(getBoABalance(driver, BoA_J.name))
        elif "boaJRewards" in request.POST:
            claimBoARewards(driver, BoA_J.name)
        elif "chaseMain" in request.POST:
            runChase(driver, Chase)
        elif "chaseLogin" in request.POST:
            locateChaseWindow(driver)
        elif "chaseBalances" in request.POST:
            Chase.setBalance(getChaseBalance(driver))
        elif "chaseRewards" in request.POST:
            claimChaseRewards(driver)
        elif "discoverMain" in request.POST:
            runDiscover(driver, Discover)
        elif "discoverLogin" in request.POST:
            locateDiscoverWindow(driver)
        elif "discoverBalances" in request.POST:
            Discover.setBalance(getDiscoverBalance(driver))
        elif "discoverRewards" in request.POST:
            claimDiscoverRewards(driver)               
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
    context = {
        'Amex': Amex,
        'Barclays': Barclays,
        'Chase': Chase,
        'Discover': Discover,
        'BoA_P': BoA_P,
        'BoA_J': BoA_J
    }
    return render(request,"scripts/creditCards.html", context)

def daily(request):
    mrAccounts = getDailyAccounts('MR')
    bankAccounts = getDailyAccounts('Bank')
    GME = getPriceInGnucash('GME')
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "bank" in request.POST:
            GME = runDailyBank(bankAccounts)
        elif "tearDown" in request.POST:
            tearDown(driver)
        elif "crypto" in request.POST:
            updateCryptoPrices(driver)
            bankAccounts['CryptoPortfolio'].updateGnuBalance(openGnuCashBook('Finance', True, True))
        elif "GME" in request.POST:
            GME = getStockPrice(driver, 'GME')
        elif "MR" in request.POST:
            runDailyMR(mrAccounts)
        elif "sofiMain" in request.POST:
            runSofi(driver, accounts)
        elif "sofiLogin" in request.POST:
            locateSofiWindow(driver)
        elif "sofiLogout" in request.POST:
            sofiLogout(driver)
        elif "sofiBalances" in request.POST:
            getSofiBalanceAndOrientPage(driver, bankAccounts['Checking'])
            getSofiBalanceAndOrientPage(driver, bankAccounts['Savings'])
        elif "allyMain" in request.POST:
            runAlly(driver, bankAccounts['Ally'])
        elif "allyLogin" in request.POST:
            locateAllyWindow(driver)
        elif "allyLogout" in request.POST:
            allyLogout(driver)        
        elif "allyBalance" in request.POST:
            Ally.setBalance(getAllyBalance(driver))
        elif "amazonMain" in request.POST:
            confirmAmazonGCBalance(driver, mrAccounts['AmazonGC'])
        elif "bingMain" in request.POST:
            locateBingWindow(driver)
        elif "bingLogin" in request.POST:
            locateBingWindow(driver)
        elif "bingActivities" in request.POST:
            bingActivities(driver)
        elif "bingBalance" in request.POST:
            mrAccounts['Bing'].setBalance(getBingBalance(driver))
            mrAccounts['Bing'].updateMRBalance(openGnuCashBook('Finance', False, False))
        elif "bingRewards" in request.POST:
            claimBingRewards(driver)
        elif "pineconeMain" in request.POST:
            runPinecone(driver, mrAccounts['Pinecone'])
        elif "pineconeLogin" in request.POST:
            locatePineconeWindow(driver)
        elif "pineconeBalance" in request.POST:
            mrAccounts['Pinecone'].setBalance(getPineConeBalance(driver))
            mrAccounts['Pinecone'].updateMRBalance(openGnuCashBook('Finance', False, False))
        elif "pineconeRewards" in request.POST:
            claimPineConeRewards(driver)
        elif "presearchMain" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(driver)
        elif "presearchLogin" in request.POST:
            locatePresearchWindow(driver)          
        elif "presearchBalance" in request.POST:
            bankAccounts['Presearch'].setBalance(getPresearchBalance(driver))
        elif "presearchSearch" in request.POST:
            searchUsingPresearch(driver)
        elif "presearchRewards" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(driver, bankAccounts['Presearch'])
        elif "swagbucksMain" in request.POST:
            runSwagbucks(driver, True, mrAccounts['Swagbucks']) if "Run Alu" in request.POST else runSwagbucks(driver, False, mrAccounts['Swagbucks'])
        elif "swagbucksLogin" in request.POST:
            locateSwagBucksWindow(driver)
        elif "swagbucksAlu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif "swagbucksContent" in request.POST:
            swagBuckscontentDiscovery(driver)
        elif "swabucksSearch" in request.POST:
            swagbucksSearch(driver)
        elif "swagbucksRewards" in request.POST:
            claimSwagBucksRewards(driver)
        elif "swagbucksInbox" in request.POST:
            swagbucksInbox(driver)
        elif "tellwutMain" in request.POST:
            runTellwut(driver, mrAccounts['Tellwut'])
        elif "tellwutLogin" in request.POST:
            locateTellWutWindow(driver)
        elif "tellwutSurveys" in request.POST:
            completeTellWutSurveys(driver)            
        elif "tellwutBalance" in request.POST:
            mrAccounts['Tellwut'].setBalance(getTellWutBalance(driver))
            mrAccounts['Tellwut'].updateMRBalance(openGnuCashBook('Finance', False, False))            
        elif "tellwutRewards" in request.POST:
            redeemTellWutRewards(driver)
        elif "paidviewpointMain" in request.POST:
            runPaidviewpoint(driver, mrAccounts['Paidviewpoint'])
        elif "paidviewpointSurvey" in request.POST:
            completePaidviewpointSurvey(driver)
        elif "paidviewpointLogin" in request.POST:
            paidviewpointLogin(driver)        
        elif "paidviewpointBalance" in request.POST:
            mrAccounts['Paidviewpoint'].setBalance(getPaidviewpointBalance(driver))
            mrAccounts['Paidviewpoint'].overwriteBalance(openGnuCashBook('Finance', False, False))            
        elif "paidviewpointRewards" in request.POST:
            redeemPaidviewpointRewards(driver)            
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))
    context = {
        'mrAccounts': mrAccounts,
        'bankAccounts': bankAccounts,
        'GME': "%.2f" % GME,
    }
    return render(request,"scripts/daily.html", context)

def discover(request):
    Discover = USD("Discover")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runDiscover(driver, Discover)
        elif "login" in request.POST:
            locateDiscoverWindow(driver)
        elif "balance" in request.POST:
            Discover.setBalance(getDiscoverBalance(driver))
        elif "rewards" in request.POST:
            claimDiscoverRewards(driver)   
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/discover"))
    context = {
        'account': Discover
    }
    return render(request,"scripts/discover.html", context)

def eternl(request):
    Cardano = Crypto("Cardano", 'ADA-Eternl')
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runEternl(driver, Cardano)
        elif "balance" in request.POST:
            Cardano.setBalance(getEternlBalance(driver))
        elif "login" in request.POST:
            locateEternlWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/eternl"))
    context = {
        'account': Cardano
    }
    return render(request,"scripts/eternl.html", context)

def exodus(request):
    Cosmos = Crypto("Cosmos")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runExodus(Cosmos)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/exodus"))
    context = {
        'account': Cosmos
    }        
    return render(request,"scripts/exodus.html", context)

def fidelity(request):
    Fidelity = USD("Fidelity")    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runFidelity(driver, Fidelity)
        elif "balance" in request.POST:
            Fidelity.setBalance(getFidelityBalance(driver))
        elif "login" in request.POST:
            locateFidelityWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/fidelity"))
    context = {
        'account': Fidelity
    }
    return render(request,"scripts/fidelity.html", context)            
    
def healthEquity(request):
    HealthEquity = USD("HSA")
    Vanguard = USD("Vanguard401k")
    HEaccounts = {
        'HealthEquity': HealthEquity, 
        'Vanguard': Vanguard
    }
    HSA_dividends = ''
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            HSA_dividends = runHealthEquity(driver, HEaccounts)
        elif "login" in request.POST:
            locateHealthEquityWindow(driver)
        elif "balance" in request.POST:
            getHealthEquityBalances(driver, HEaccounts)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/healthEquity"))
    context = {
        'HEaccounts': HEaccounts,
        'HSA_dividends': HSA_dividends
        }
    return render(request,"scripts/healthEquity.html", context)

def ioPay(request):
    IoTex = Crypto("IoTex")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runIoPay(driver, IoTex)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/iopay"))
    context = {
        'account': IoTex
    }
    return render(request,"scripts/iopay.html", context)

def kraken(request):
    Ethereum2 = Crypto("Ethereum2")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runKraken(driver, Ethereum2)
        elif "balance" in request.POST:
            Ethereum2.setBalance(getKrakenBalance(driver))
        elif "login" in request.POST:
            locateKrakenWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/kraken"))
    context = {
            'account': Ethereum2
        }        
    return render(request,"scripts/kraken.html", context)        

def ledger(request):
    coinList = getLedgerAccounts()
    if request.method == 'POST':
        if "main" in request.POST:
            runLedger(coinList)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/ledger"))
    context = {
        'coinList': coinList
    }
    return render(request,"scripts/ledger.html", context)

def monthly(request):
    usdAccounts = getMonthlyAccounts('USD')
    cryptoAccounts = getMonthlyAccounts('Crypto')
    HSA_dividends = ''
    if request.method == 'POST':
        driver = Driver("Chrome")
        today = datetime.today()
        if "USD" in request.POST:
            runUSD(driver, today, usdAccounts)
        elif "prices" in request.POST:
            updateInvestmentPrices(driver)
        elif "Crypto" in request.POST:
            runCrypto(driver, today, cryptoAccounts)
        elif "fidelityMain" in request.POST:
            runFidelity(driver, Fidelity)
        elif "fidelityBalance" in request.POST:
            usdAccounts['Fidelity'].setBalance(getFidelityBalance(driver))
        elif "fidelityLogin" in request.POST:
            locateFidelityWindow(driver)
        elif "HEMain" in request.POST:
            HSA_dividends = runHealthEquity(driver, {'HealthEquity': usdAccounts['HealthEquity'], 'Vanguard': usdAccounts['V401k']})
        elif "HELogin" in request.POST:
            locateHealthEquityWindow(driver)
        elif "HEBalances" in request.POST:
            getHealthEquityBalances(driver, {'HealthEquity': usdAccounts['HealthEquity'], 'Vanguard': usdAccounts['V401k']})
        elif "vanguardLogin" in request.POST:
            locateVanguardWindow(driver)
        elif "vanguardBalances" in request.POST:
            getVanguardBalanceAndInterestYTD(driver, [usdAccounts['Pension'], usdAccounts['V401k']])
        elif "worthyBalance" in request.POST:
            getWorthyBalance(driver, usdAccounts['Worthy'])
        elif "worthyLogin" in request.POST:
            locateWorthyWindow(driver)
        elif "coinbaseMain" in request.POST:
            runCoinbase(driver, [cryptoAccounts['Loopring']])
        elif "coinbaseLogin" in request.POST:
            locateCoinbaseWindow(driver)
        elif "coinbaseBalance" in request.POST:
            getCoinbaseBalances(driver, [cryptoAccounts['Loopring']])
        elif "eternlMain" in request.POST:
            runEternl(driver, cryptoAccounts['Cardano'])
        elif "eternlBalance" in request.POST:
            cryptoAccounts['Cardano'].setBalance(getEternlBalance(driver))
        elif "eternlLogin" in request.POST:
            locateEternlWindow(driver)
        elif "exodusMain" in request.POST:
            runExodus(cryptoAccounts['Cosmos'])
        elif "ioPayMain" in request.POST:
            runIoPay(driver, cryptoAccounts['IoTex'])
        elif "krakenMain" in request.POST:
            runKraken(driver, cryptoAccounts['Ethereum2'])
        elif "krakenBalance" in request.POST:
            cryptoAccounts['Ethereum2'].setBalance(getKrakenBalance(driver))
        elif "krakenLogin" in request.POST:
            locateKrakenWindow(driver)
        elif "ledgerMain" in request.POST:
            runLedger(cryptoAccounts['ledgerAccounts'])            
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/monthly"))
    context = {
        'usdAccounts': usdAccounts,
        'cryptoAccounts': cryptoAccounts,
        'HSA_dividends': HSA_dividends,
    }
    return render(request,"scripts/monthly.html", context)

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
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/myConstant"))
    return render(request,"scripts/myconstant.html")

def paidviewpoint(request):
    Paidviewpoint = USD("Paidviewpoint")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPaidviewpoint(driver, Paidviewpoint)
        if "survey" in request.POST:
            completePaidviewpointSurvey(driver)
        elif "login" in request.POST:
            paidviewpointLogin(driver)        
        elif "balance" in request.POST:
            Paidviewpoint.setBalance(getPaidviewpointBalance(driver))
            Paidviewpoint.overwriteBalance(openGnuCashBook('Finance', False, False))            
        elif "rewards" in request.POST:
            redeemPaidviewpointRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paidviewpoint"))
    context = {
        'Paidviewpoint': Paidviewpoint
    }
    return render(request,"scripts/paidviewpoint.html", context)

def paypal(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
    if "main" in request.POST:
        runPaypal(driver)
    elif "login" in request.POST:
        locatePayPalWindow(driver)
    elif "close windows" in request.POST:
        driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paypal"))        
    return render(request,"scripts/paypal.html")

def pinecone(request):
    Pinecone = Crypto("Pinecone")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPinecone(driver, Pinecone)
        elif "login" in request.POST:
            locatePineconeWindow(driver)
        elif "balance" in request.POST:
            Pinecone.setBalance(getPineConeBalance(driver))
        elif "rewards" in request.POST:
            claimPineConeRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pinecone"))
    context = {
        'Pinecone': Pinecone
    }
    return render(request,"scripts/pinecone.html", context)

def presearch(request):
    Presearch = Crypto("Presearch")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(driver)
        elif "login" in request.POST:
            locatePresearchWindow(driver)          
        elif "balance" in request.POST:
            Presearch.setBalance(getPresearchBalance(driver))
        elif "search" in request.POST:
            searchUsingPresearch(driver)
        elif "rewards" in request.POST:
            presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/presearch"))
    context = {
            'account': Presearch
        }             
    return render(request,"scripts/presearch.html", context)

def psCoupons(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPSCoupon(driver)
        elif "login" in request.POST:
            locatePSCouponWindow(driver)         
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pscoupons"))             
    return render(request,"scripts/pscoupons.html")

def sofi(request):
    Checking = USD("Sofi Checking")
    Savings = USD("Sofi Savings")
    accounts = [Checking, Savings]    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runSofi(driver, accounts)
        elif "login" in request.POST:
            locateSofiWindow(driver)
        elif "logout" in request.POST:
            sofiLogout(driver)            
        elif "balances" in request.POST:
            getSofiBalanceAndOrientPage(driver, Checking)
            getSofiBalanceAndOrientPage(driver, Savings)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/sofi"))       
    context = {
        'Checking': Checking,
        'Savings': Savings
    }
    return render(request,"scripts/sofi.html", context)

def swagbucks(request):
    Swagbucks = Crypto("Swagbucks")
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runSwagbucks(driver, True, Swagbucks) if "Run Alu" in request.POST else runSwagbucks(driver, False, Swagbucks)
        elif "login" in request.POST:
            locateSwagBucksWindow(driver)
        elif "alu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif "content" in request.POST:
            swagBuckscontentDiscovery(driver)
        elif "search" in request.POST:
            swagbucksSearch(driver)
        elif "rewards" in request.POST:
            claimSwagBucksRewards(driver)
        elif "inbox" in request.POST:
            swagbucksInbox(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/swagbucks"))                   
    return render(request,"scripts/swagbucks.html")

def tellwut(request):
    Tellwut = Crypto("Tellwut")    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runTellwut(driver, Tellwut)
        elif "login" in request.POST:
            locateTellWutWindow(driver)
        elif "surveys" in request.POST:
            completeTellWutSurveys(driver)
        elif "balance" in request.POST:
            Tellwut.setBalance(getTellWutBalance(driver))
            Tellwut.updateMRBalance(openGnuCashBook('Finance', False, False))
        elif "rewards" in request.POST:
            redeemTellWutRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/tellwut"))
    context = {
        'Tellwut': Tellwut
    }
    return render(request,"scripts/tellwut.html", context)

def updateGoals(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()        
        if "main" in request.POST:
            account = body.get("accounts")
            timeframe = body.get("TimeFrame")
            runUpdateGoals(account, timeframe)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/updateGoals"))      
    return render(request,"scripts/updateGoals.html")

def vanguard(request):
    Pension = USD("VanguardPension")
    V401k = USD("Vanguard401k")
    accounts = [Pension, V401k]
    pensionInterest = ""
    pensionContributions = ""
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            interestAndEmployerContribution = runVanguard(driver, accounts)
            pensionInterest = str(interestAndEmployerContribution[0])
            pensionContributions = str(interestAndEmployerContribution[1])
        elif "login" in request.POST:
            locateVanguardWindow(driver)
        elif "balance" in request.POST:
            getVanguardBalanceAndInterestYTD(driver, accounts)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/vanguard"))
    context = {
        'Pension': Pension,
        'PensionInterest': pensionInterest,
        'PensionContributions': pensionContributions,
        'V401k': V401k,
    }            
    return render(request,"scripts/vanguard.html", context)

def worthy(request):
    context = dict()
    Worthy = USD("Worthy")    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "balance" in request.POST:
            getWorthyBalance(driver, Worthy)
        elif "login" in request.POST:
            locateWorthyWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/worthy"))
    context = {
            'account': Worthy
        }            
    return render(request,"scripts/worthy.html", context)
