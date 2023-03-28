from datetime import datetime
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
from scripts.scripts.Functions.GnuCashFunctions import getPriceInGnucash

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
    context = {'bank':bank, 'cc':cc, 'crypto':crypto, 'mr':mr}
    return render(request,"scripts/scripts.html", context)

def ally(request):
    readBook = openGnuCashBook('Home', True, True)
    Ally = USD("Ally", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Home', False, False)        
        if "main" in request.POST:
            runAlly(driver, Ally, writeBook)
        elif "login" in request.POST:
            locateAllyWindow(driver)
        elif "logout" in request.POST:
            allyLogout(driver)
        elif "balance" in request.POST:
            Ally.setBalance(getAllyBalance(driver))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Ally}
    readBook.close()
    return render(request,"scripts/ally.html", context)

def amazon(request):
    readBook = openGnuCashBook('Finance', True, True)
    AmazonGC = USD("AmazonGC", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            confirmAmazonGCBalance(driver, AmazonGC)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amazon"))
    context = {'AmazonGC': AmazonGC}
    readBook.close()
    return render(request,"scripts/amazon.html", context)

def amex(request):
    readBook = openGnuCashBook('Finance', True, True)
    Amex = USD("Amex", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Home', False, False)
        if "main" in request.POST:
            runAmex(driver, Amex, writeBook)
        elif "login" in request.POST:
            locateAmexWindow(driver)
        elif "balance" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "rewards" in request.POST:
            claimAmexRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amex"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Amex}
    readBook.close()
    return render(request,"scripts/amex.html", context)

def barclays(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Barclays = USD("Barclays", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Home', False, False)
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Barclays}
    readBook.close()
    return render(request,"scripts/barclays.html", context)

def bing(request):
    readBook = openGnuCashBook('Finance', True, True)
    Bing = Crypto("Bing", readBook)
    Bing.getData()
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "main" in request.POST:
            runBing(driver, Bing, writeBook)
        elif "login" in request.POST:
            bingLogin(driver)
        elif "activities" in request.POST:
            bingActivities(driver)
        elif "balance" in request.POST:
            Bing.setBalance(getBingBalance(driver))
            Bing.updateMRBalance(writeBook)
        elif "rewards" in request.POST:
            claimBingRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/bing"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Bing': Bing}
    readBook.close()
    return render(request,"scripts/bing.html", context)

def boa(request):
    personalReadBook = openGnuCashBook('Finance', True, True)
    jointReadBook = openGnuCashBook('Home', True, True)
    Personal = USD("BoA", personalReadBook)
    Joint = USD("BoA-joint", jointReadBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        account = body.get("account")
        bookName = 'Finance' if account == 'Personal' else 'Home'
        book = openGnuCashBook(bookName, False, False)
        if "main" in request.POST:
            runBoA(driver, Personal, book) if account == 'Personal' else runBoA(driver, Joint, book)
        elif "login" in request.POST:
            locateBoAWindowAndOpenAccount(driver, account)
        elif "balance" in request.POST:
            Personal.setBalance(getBoABalance(driver, account)) if account == 'Personal' else Joint.setBalance(getBoABalance(driver, account))
        elif "rewards" in request.POST:
            claimBoARewards(driver, account)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/boa"))
        book.close()
    context = {'Personal': Personal, 'Joint': Joint}
    personalReadBook.close()
    jointReadBook.close()
    return render(request,"scripts/boa.html", context)

def chase(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Chase = USD("Chase", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Chase}
    readBook.close()
    return render(request,"scripts/chase.html", context)

def coinbase(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Loopring = Crypto("Loopring", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "main" in request.POST:
            runCoinbase(driver, [Loopring], writeBook)
        elif "login" in request.POST:
            locateCoinbaseWindow(driver)
        elif "balance" in request.POST:
            getCoinbaseBalances(driver, [Loopring])
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/coinbase"))      
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Loopring': Loopring}
    readBook.close()
    return render(request,"scripts/coinbase.html", context)

def creditCards(request):
    personalReadBook = openGnuCashBook('Finance', True, True)
    jointReadBook = openGnuCashBook('Home', True, True)    
    Amex = USD("Amex", personalReadBook)
    Barclays = USD("Barclays", personalReadBook)
    Chase = USD("Chase", personalReadBook)
    Discover = USD("Discover", personalReadBook)
    BoA_P = USD("BoA", personalReadBook)
    BoA_J = USD("BoA-joint", jointReadBook)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        bookName = 'Home' if 'boaJ' in request.POST else 'Finance'
        writeBook = openGnuCashBook(bookName, False, False)
        if "amexMain" in request.POST:
            runAmex(driver, Amex, writeBook)
        elif "amexLogin" in request.POST:
            locateAmexWindow(driver)
        elif "amexBalances" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "amexRewards" in request.POST:
            claimAmexRewards(driver)
        elif "barclaysMain" in request.POST:
            runBarclays(driver, Barclays, writeBook)
        elif "barclaysLogin" in request.POST:
            locateBarclaysWindow(driver)
        elif "barclaysBalances" in request.POST:
            Barclays.setBalance(getBarclaysBalance(driver))
        elif "barclaysRewards" in request.POST:
            claimBarclaysRewards(driver)
        elif "boaPMain" in request.POST:
            runBoA(driver, BoA_P, writeBook)
        elif "boaPLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_P.name)
        elif "boaPBalances" in request.POST:
            BoA_P.setBalance(getBoABalance(driver, BoA_P.name))
        elif "boaPRewards" in request.POST:
            claimBoARewards(driver, BoA_P.name)
        elif "boaJMain" in request.POST:
            runBoA(driver, BoA_J, writeBook)
        elif "boaJLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_J.name)
        elif "boaJBalances" in request.POST:
            BoA_J.setBalance(getBoABalance(driver, BoA_J.name))
        elif "boaJRewards" in request.POST:
            claimBoARewards(driver, BoA_J.name)
        elif "chaseMain" in request.POST:
            runChase(driver, Chase, writeBook)
        elif "chaseLogin" in request.POST:
            locateChaseWindow(driver)
        elif "chaseBalances" in request.POST:
            Chase.setBalance(getChaseBalance(driver))
        elif "chaseRewards" in request.POST:
            claimChaseRewards(driver)
        elif "discoverMain" in request.POST:
            runDiscover(driver, Discover, writeBook)
        elif "discoverLogin" in request.POST:
            locateDiscoverWindow(driver)
        elif "discoverBalances" in request.POST:
            Discover.setBalance(getDiscoverBalance(driver))
        elif "discoverRewards" in request.POST:
            claimDiscoverRewards(driver)               
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Amex': Amex, 'Barclays': Barclays, 'Chase': Chase, 'Discover': Discover, 'BoA_P': BoA_P, 'BoA_J': BoA_J}
    personalReadBook.close()
    jointReadBook.close()
    return render(request,"scripts/creditCards.html", context)

def daily(request):
    personalReadBook = openGnuCashBook('Finance', True, True)
    jointReadBook = openGnuCashBook('Home', True, True)
    mrAccounts = getDailyAccounts('MR', personalReadBook)
    bankAccounts = getDailyAccounts('Bank', personalReadBook, jointReadBook)
    GME = getPriceInGnucash('GME', personalReadBook, datetime.today().date())
    if request.method == 'POST':
        driver = Driver("Chrome")
        personalWriteBook = openGnuCashBook('Finance', False, False)
        if "bank" in request.POST or "ally" in request.POST:
            jointWriteBook = openGnuCashBook('Home', False, False)
            if "bank" in request.POST:
                GME = runDailyBank(bankAccounts, personalWriteBook, jointWriteBook)
            elif "allyMain" in request.POST:
                runAlly(driver, bankAccounts['Ally'], jointWriteBook)
            elif "allyLogin" in request.POST:
                locateAllyWindow(driver)
            elif "allyLogout" in request.POST:
                allyLogout(driver)        
            elif "allyBalance" in request.POST:
                Ally.setBalance(getAllyBalance(driver))
            if not jointWriteBook.is_saved:
                jointWriteBook.save()
            jointWriteBook.close()
        elif "paypal" in request.POST:
            runPaypal(driver)
        elif "tearDown" in request.POST:
            tearDown(driver)
        elif "crypto" in request.POST:
            updateCryptoPrices(driver, personalWriteBook)
            bankAccounts['CryptoPortfolio'].updateGnuBalance(personalWriteBook)
        elif "GME" in request.POST:
            GME = getStockPrice(driver, 'GME')
            updatePriceInGnucash('GME', GME, personalWriteBook)
        elif "MR" in request.POST:
            runDailyMR(mrAccounts, personalWriteBook)
        elif "sofiMain" in request.POST:
            runSofi(driver, accounts)
        elif "sofiLogin" in request.POST:
            locateSofiWindow(driver)
        elif "sofiLogout" in request.POST:
            sofiLogout(driver)
        elif "sofiBalances" in request.POST:
            getSofiBalanceAndOrientPage(driver, bankAccounts['Checking'])
            getSofiBalanceAndOrientPage(driver, bankAccounts['Savings'])
        elif "amazonMain" in request.POST:
            confirmAmazonGCBalance(driver, mrAccounts['AmazonGC'])
        elif "bingMain" in request.POST:
            runBing(driver, mrAccounts['Bing'], personalWriteBook)
        elif "bingLogin" in request.POST:
            locateBingWindow(driver)
        elif "bingActivities" in request.POST:
            bingActivities(driver)
        elif "bingBalance" in request.POST:
            mrAccounts['Bing'].setBalance(getBingBalance(driver))
            mrAccounts['Bing'].updateMRBalance(personalWriteBook)
        elif "bingRewards" in request.POST:
            claimBingRewards(driver)
        elif "pineconeMain" in request.POST:
            runPinecone(driver, mrAccounts['Pinecone'], personalWriteBook)
        elif "pineconeLogin" in request.POST:
            locatePineconeWindow(driver)
        elif "pineconeBalance" in request.POST:
            mrAccounts['Pinecone'].setBalance(getPineConeBalance(driver))
            mrAccounts['Pinecone'].updateMRBalance(personalWriteBook)
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
            runSwagbucks(driver, True, mrAccounts['Swagbucks'], personalWriteBook) if "Run Alu" in request.POST else runSwagbucks(driver, False, mrAccounts['Swagbucks'], personalWriteBook)
        elif "swagbucksLogin" in request.POST:
            locateSwagBucksWindow(driver)
        elif "swagbucksAlu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif 'swagbucksBalance' in request.POST:
            mrAccounts['Swagbucks'].setBalance(getSwagBucksBalance(driver))
            mrAccounts['Swagbucks'].updateMRBalance(personalWriteBook)
        elif "swagbucksContent" in request.POST:
            swagBuckscontentDiscovery(driver)
        elif "swabucksSearch" in request.POST:
            swagbucksSearch(driver)
        elif "swagbucksRewards" in request.POST:
            claimSwagBucksRewards(driver)
        elif "swagbucksInbox" in request.POST:
            swagbucksInbox(driver)
        elif "tellwutMain" in request.POST:
            runTellwut(driver, mrAccounts['Tellwut'], personalWriteBook)
        elif "tellwutLogin" in request.POST:
            locateTellWutWindow(driver)
        elif "tellwutSurveys" in request.POST:
            completeTellWutSurveys(driver)            
        elif "tellwutBalance" in request.POST:
            mrAccounts['Tellwut'].setBalance(getTellWutBalance(driver))
            mrAccounts['Tellwut'].updateMRBalance(personalWriteBook)            
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
        if not personalWriteBook.is_saved:
            personalWriteBook.save()
        personalWriteBook.close()
    context = {'mrAccounts': mrAccounts, 'bankAccounts': bankAccounts, 'GME': "%.2f" % GME}
    personalReadBook.close()
    jointReadBook.close()
    return render(request,"scripts/daily.html", context)

def discover(request):
    readBook = openGnuCashBook('Finance', True, True)
    Discover = USD("Discover", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {
        'account': Discover
    }
    readBook.close()
    return render(request,"scripts/discover.html", context)

def eternl(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Cardano = Crypto("Cardano", readBook, 'ADA-Eternl')
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runEternl(driver, Cardano)
        elif "balance" in request.POST:
            Cardano.setBalance(getEternlBalance(driver))
        elif "login" in request.POST:
            locateEternlWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/eternl"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Cardano}
    readBook.close()
    return render(request,"scripts/eternl.html", context)

def exodus(request):
    readBook = openGnuCashBook('Finance', True, True)        
    Cosmos = Crypto("Cosmos", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runExodus(Cosmos)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/exodus"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Cosmos}
    readBook.close()
    return render(request,"scripts/exodus.html", context)

def fidelity(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Fidelity = USD("Fidelity", readBook)    
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
    context = {'account': Fidelity}
    readBook.close()
    return render(request,"scripts/fidelity.html", context)            
    
def healthEquity(request):
    readBook = openGnuCashBook('Finance', True, True)
    HealthEquity = USD("HSA", readBook)
    Vanguard = USD("Vanguard401k", readBook)
    HEaccounts = {'HealthEquity': HealthEquity, 'Vanguard': Vanguard}
    HSA_dividends = ''
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            HSA_dividends = runHealthEquity(driver, HEaccounts)
        elif "login" in request.POST:
            locateHealthEquityWindow(driver)
        elif "balance" in request.POST:
            getHealthEquityBalances(driver, HEaccounts)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/healthEquity"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'HEaccounts': HEaccounts, 'HSA_dividends': HSA_dividends}
    readBook.close()
    return render(request,"scripts/healthEquity.html", context)

def ioPay(request):
    readBook = openGnuCashBook('Finance', True, True)
    IoTex = Crypto("IoTex", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runIoPay(driver, IoTex)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/iopay"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': IoTex}
    readBook.close()
    return render(request,"scripts/iopay.html", context)

def kraken(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Ethereum2 = Crypto("Ethereum2", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "main" in request.POST:
            runKraken(driver, Ethereum2)
        elif "balance" in request.POST:
            Ethereum2.setBalance(getKrakenBalance(driver))
        elif "login" in request.POST:
            locateKrakenWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/kraken"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Ethereum2}
    readBook.close()
    return render(request,"scripts/kraken.html", context)        

def ledger(request):
    readBook = openGnuCashBook('Finance', True, True)    
    coinList = getLedgerAccounts(readBook)
    if request.method == 'POST':
        if "main" in request.POST:
            writeBook = openGnuCashBook('Finance', False, False)
            runLedger(coinList)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/ledger"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'coinList': coinList}
    readBook.close()
    return render(request,"scripts/ledger.html", context)

def monthly(request):
    readBook = openGnuCashBook('Finance', True, True)
    usdAccounts = getMonthlyAccounts('USD', readBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', readBook)
    HSA_dividends = ''
    if request.method == 'POST':
        driver = Driver("Chrome")
        today = datetime.today()
        writeBook = openGnuCashBook('Finance', False, False)
        if "USD" in request.POST:
            runUSD(driver, today, usdAccounts, writeBook)
        elif "prices" in request.POST:
            Home = USD("Home")
            updateInvestmentPrices(driver, Home)
        elif "Crypto" in request.POST:
            runCrypto(driver, today, cryptoAccounts, writeBook)
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
            runCoinbase(driver, [cryptoAccounts['Loopring']], writeBook)
        elif "coinbaseLogin" in request.POST:
            locateCoinbaseWindow(driver)
        elif "coinbaseBalance" in request.POST:
            getCoinbaseBalances(driver, [cryptoAccounts['Loopring']])
        elif "eternlMain" in request.POST:
            runEternl(driver, cryptoAccounts['Cardano'], writeBook)
        elif "eternlBalance" in request.POST:
            cryptoAccounts['Cardano'].setBalance(getEternlBalance(driver))
        elif "eternlLogin" in request.POST:
            locateEternlWindow(driver)
        elif "exodusMain" in request.POST:
            runExodus(cryptoAccounts['Cosmos'], writeBook)
        elif "ioPayMain" in request.POST:
            runIoPay(driver, cryptoAccounts['IoTex'])
        elif "krakenMain" in request.POST:
            runKraken(driver, cryptoAccounts['Ethereum2'], writeBook)
        elif "krakenBalance" in request.POST:
            cryptoAccounts['Ethereum2'].setBalance(getKrakenBalance(driver))
        elif "krakenLogin" in request.POST:
            locateKrakenWindow(driver)
        elif "ledgerMain" in request.POST:
            runLedger(cryptoAccounts['ledgerAccounts'], writeBook)            
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/monthly"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'usdAccounts': usdAccounts, 'cryptoAccounts': cryptoAccounts, 'HSA_dividends': HSA_dividends}
    readBook.close()
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
    readBook = openGnuCashBook('Finance', True, True)
    Paidviewpoint = USD("Paidviewpoint", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "main" in request.POST:
            runPaidviewpoint(driver, Paidviewpoint, writeBook)
        if "survey" in request.POST:
            completePaidviewpointSurvey(driver)
        elif "login" in request.POST:
            paidviewpointLogin(driver)        
        elif "balance" in request.POST:
            Paidviewpoint.setBalance(getPaidviewpointBalance(driver))
            Paidviewpoint.overwriteBalance(writeBook)
        elif "rewards" in request.POST:
            redeemPaidviewpointRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paidviewpoint"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Paidviewpoint': Paidviewpoint}
    readBook.close()
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
    readBook = openGnuCashBook('Finance', True, True)    
    Pinecone = Crypto("Pinecone", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runPinecone(driver, Pinecone, writeBook)
        elif "login" in request.POST:
            locatePineconeWindow(driver)
        elif "balance" in request.POST:
            Pinecone.setBalance(getPineConeBalance(driver))
            Pinecone.updateMRBalance(writeBook)    
        elif "rewards" in request.POST:
            claimPineConeRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pinecone"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Pinecone': Pinecone}
    readBook.close()
    return render(request,"scripts/pinecone.html", context)

def presearch(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Presearch = Crypto("Presearch", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Presearch}
    readBook.close()
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
    readBook = openGnuCashBook('Finance', True, True)    
    Checking = USD("Sofi Checking", readBook)
    Savings = USD("Sofi Savings", readBook)
    accounts = [Checking, Savings]    
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Checking': Checking, 'Savings': Savings}
    readBook.close()
    return render(request,"scripts/sofi.html", context)

def swagbucks(request):
    readBook = openGnuCashBook('Finance', True, True)    
    Swagbucks = Crypto("Swagbucks", readBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runSwagbucks(driver, True, Swagbucks, writeBook) if "Run Alu" in request.POST else runSwagbucks(driver, False, Swagbucks, writeBook)
        elif "login" in request.POST:
            locateSwagBucksWindow(driver)
        elif "alu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif 'balance' in request.POST:
            Swagbucks.setBalance(getSwagBucksBalance(driver))
            Swagbucks.updateMRBalance(writeBook)            
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Swagbucks}
    readBook.close()
    return render(request,"scripts/swagbucks.html", context)

def tellwut(request):
    readBook = openGnuCashBook('Finance', True, True)
    Tellwut = Crypto("Tellwut", readBook)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)        
        if "main" in request.POST:
            runTellwut(driver, Tellwut)
        elif "login" in request.POST:
            print(driver.webDriver.current_window_handle)
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
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Tellwut': Tellwut}
    readBook.close()
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
    readBook = openGnuCashBook('Finance', True, True)    
    Pension = USD("VanguardPension", readBook)
    V401k = USD("Vanguard401k", readBook)
    accounts = [Pension, V401k]
    pensionInterest = ""
    pensionContributions = ""
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "main" in request.POST:
            interestAndEmployerContribution = runVanguard(driver, accounts)
            pensionInterest = str(interestAndEmployerContribution['interest'])
            pensionContributions = str(interestAndEmployerContribution['employerContribution'])
        elif "login" in request.POST:
            locateVanguardWindow(driver)
        elif "balance" in request.POST:
            getVanguardBalanceAndInterestYTD(driver, accounts)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/vanguard"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'Pension': Pension, 'PensionInterest': pensionInterest, 'PensionContributions': pensionContributions, 'V401k': V401k}
    readBook.close()        
    return render(request,"scripts/vanguard.html", context)

def worthy(request):
    readBook = openGnuCashBook('Finance', True, True)
    Worthy = USD("Worthy", readBook)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        writeBook = openGnuCashBook('Finance', False, False)
        if "balance" in request.POST:
            getWorthyBalance(driver, Worthy)
        elif "login" in request.POST:
            locateWorthyWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/worthy"))
        if not writeBook.is_saved:
            writeBook.save()
        writeBook.close()
    context = {'account': Worthy}
    readBook.close()
    return render(request,"scripts/worthy.html", context)
