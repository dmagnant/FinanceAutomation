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
from scripts.scripts.Classes.GnuCash import GnuCash

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
    book = GnuCash('Home')
    Ally = USD("Ally", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runAlly(driver, Ally, book)
        elif "login" in request.POST:
            locateAllyWindow(driver)
        elif "logout" in request.POST:
            allyLogout(driver)
        elif "balance" in request.POST:
            Ally.setBalance(getAllyBalance(driver))
    context = {'account': Ally}
    book.closeBook()
    return render(request,"scripts/ally.html", context)

def amazon(request):
    book = GnuCash('Finance')
    AmazonGC = USD("AmazonGC", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            confirmAmazonGCBalance(driver, AmazonGC)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amazon"))
    context = {'AmazonGC': AmazonGC}
    book.closeBook()
    return render(request,"scripts/amazon.html", context)

def amex(request):
    book = GnuCash('Finance')
    Amex = USD("Amex", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runAmex(driver, Amex, book)
        elif "login" in request.POST:
            locateAmexWindow(driver)
        elif "balance" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "rewards" in request.POST:
            claimAmexRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amex"))
    context = {'account': Amex}
    book.closeBook()
    return render(request,"scripts/amex.html", context)

def barclays(request):
    book = GnuCash('Finance')
    Barclays = USD("Barclays", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runBarclays(driver, Barclays, book)
        elif "login" in request.POST:
            locateBarclaysWindow(driver)
        elif "balance" in request.POST:
            Barclays.setBalance(getBarclaysBalance(driver))
        elif "rewards" in request.POST:
            claimBarclaysRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
    context = {'account': Barclays}
    book.closeBook()
    return render(request,"scripts/barclays.html", context)

def bing(request):
    book = GnuCash('Finance')
    Bing = Crypto("Bing", book)
    Bing.getData()
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runBing(driver, Bing, book)
        elif "login" in request.POST:
            bingLogin(driver)
        elif "activities" in request.POST:
            bingActivities(driver)
        elif "balance" in request.POST:
            Bing.setBalance(getBingBalance(driver))
            book.updateMRBalance(Bing)
        elif "rewards" in request.POST:
            claimBingRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/bing"))
    context = {'Bing': Bing}
    book.closeBook()
    return render(request,"scripts/bing.html", context)

def boa(request):
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    Personal = USD("BoA", personalBook)
    Joint = USD("BoA-joint", jointBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        account = body.get("account")
        if "main" in request.POST:
            runBoA(driver, Personal, personalBook) if account == 'Personal' else runBoA(driver, Joint, jointBook)
        elif "login" in request.POST:
            locateBoAWindowAndOpenAccount(driver, account)
        elif "balance" in request.POST:
            Personal.setBalance(getBoABalance(driver, account)) if account == 'Personal' else Joint.setBalance(getBoABalance(driver, account))
        elif "rewards" in request.POST:
            claimBoARewards(driver, account)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/boa"))
    context = {'Personal': Personal, 'Joint': Joint}
    personalBook.closeBook()
    jointBook.closeBook()
    return render(request,"scripts/boa.html", context)

def chase(request):
    book = GnuCash('Finance')
    Chase = USD("Chase", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runChase(driver, Chase, book)
        elif "login" in request.POST:
            locateChaseWindow(driver)
        elif "balance" in request.POST:
            Chase.setBalance(getChaseBalance(driver))
        elif "rewards" in request.POST:
            claimChaseRewards(driver)   
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/chase"))
    context = {'account': Chase}
    book.closeBook()
    return render(request,"scripts/chase.html", context)

def coinbase(request):
    book = GnuCash('Finance')
    Loopring = Crypto("Loopring", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runCoinbase(driver, [Loopring], book)
        elif "login" in request.POST:
            locateCoinbaseWindow(driver)
        elif "balance" in request.POST:
            getCoinbaseBalances(driver, [Loopring])
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/coinbase"))      
    context = {'Loopring': Loopring}
    book.closeBook()
    return render(request,"scripts/coinbase.html", context)

def creditCards(request):
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home') 
    Amex = USD("Amex", personalBook)
    Barclays = USD("Barclays", personalBook)
    Chase = USD("Chase", personalBook)
    Discover = USD("Discover", personalBook)
    BoA_P = USD("BoA", personalBook)
    BoA_J = USD("BoA-joint", jointBook)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        bookName = 'Home' if 'boaJ' in request.POST else 'Finance'
        if "amexMain" in request.POST:
            runAmex(driver, Amex, personalBook)
        elif "amexLogin" in request.POST:
            locateAmexWindow(driver)
        elif "amexBalances" in request.POST:
            Amex.setBalance(getAmexBalance(driver))
        elif "amexRewards" in request.POST:
            claimAmexRewards(driver)
        elif "barclaysMain" in request.POST:
            runBarclays(driver, Barclays, personalBook)
        elif "barclaysLogin" in request.POST:
            locateBarclaysWindow(driver)
        elif "barclaysBalances" in request.POST:
            Barclays.setBalance(getBarclaysBalance(driver))
        elif "barclaysRewards" in request.POST:
            claimBarclaysRewards(driver)
        elif "boaPMain" in request.POST:
            runBoA(driver, BoA_P, personalBook)
        elif "boaPLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_P.name)
        elif "boaPBalances" in request.POST:
            BoA_P.setBalance(getBoABalance(driver, BoA_P.name))
        elif "boaPRewards" in request.POST:
            claimBoARewards(driver, BoA_P.name)
        elif "boaJMain" in request.POST:
            runBoA(driver, BoA_J, jointBook)
        elif "boaJLogin" in request.POST:
            locateBoAWindowAndOpenAccount(driver, BoA_J.name)
        elif "boaJBalances" in request.POST:
            BoA_J.setBalance(getBoABalance(driver, BoA_J.name))
        elif "boaJRewards" in request.POST:
            claimBoARewards(driver, BoA_J.name)
        elif "chaseMain" in request.POST:
            runChase(driver, Chase, personalBook)
        elif "chaseLogin" in request.POST:
            locateChaseWindow(driver)
        elif "chaseBalances" in request.POST:
            Chase.setBalance(getChaseBalance(driver))
        elif "chaseRewards" in request.POST:
            claimChaseRewards(driver)
        elif "discoverMain" in request.POST:
            runDiscover(driver, Discover, personalBook)
        elif "discoverLogin" in request.POST:
            locateDiscoverWindow(driver)
        elif "discoverBalances" in request.POST:
            Discover.setBalance(getDiscoverBalance(driver))
        elif "discoverRewards" in request.POST:
            claimDiscoverRewards(driver)               
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
    context = {'Amex': Amex, 'Barclays': Barclays, 'Chase': Chase, 'Discover': Discover, 'BoA_P': BoA_P, 'BoA_J': BoA_J}
    personalBook.closeBook()
    jointBook.closeBook()
    return render(request,"scripts/creditCards.html", context)

def daily(request):
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home') 
    mrAccounts = getDailyAccounts('MR', personalBook)
    bankAccounts = getDailyAccounts('Bank', personalBook, jointBook)
    GME = personalBook.getPriceInGnucash('GME', datetime.today().date())
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "bank" in request.POST:
            GME = runDailyBank(bankAccounts, personalBook, jointBook)
        elif "allyMain" in request.POST:
            runAlly(driver, bankAccounts['Ally'], jointBook)
        elif "allyLogin" in request.POST:
            locateAllyWindow(driver)
        elif "allyLogout" in request.POST:
            allyLogout(driver)        
        elif "allyBalance" in request.POST:
            bankAccounts['Ally'].setBalance(getAllyBalance(driver))
        elif "paypal" in request.POST:
            runPaypal(driver)
        elif "tearDown" in request.POST:
            tearDown(driver)
        elif "crypto" in request.POST:
            updateCryptoPrices(driver, personalBook)
            bankAccounts['CryptoPortfolio'].updateGnuBalance(personalBook.getBalance(bankAccounts['CryptoPortfolio'].gnuAccount))
        elif "GME" in request.POST:
            GME = getStockPrice(driver, 'GME')
            personalBook.updatePriceInGnucash('GME', GME)
        elif "MR" in request.POST:
            runDailyMR(mrAccounts, personalBook)
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
            runBing(driver, mrAccounts['Bing'], personalBook)
        elif "bingLogin" in request.POST:
            locateBingWindow(driver)
        elif "bingActivities" in request.POST:
            bingActivities(driver)
        elif "bingBalance" in request.POST:
            mrAccounts['Bing'].setBalance(getBingBalance(driver))
            personalBook.updateMRBalance(mrAccounts['Bing'])
        elif "bingRewards" in request.POST:
            claimBingRewards(driver)
        elif "pineconeMain" in request.POST:
            runPinecone(driver, mrAccounts['Pinecone'], personalBook)
        elif "pineconeLogin" in request.POST:
            locatePineconeWindow(driver)
        elif "pineconeBalance" in request.POST:
            mrAccounts['Pinecone'].setBalance(getPineConeBalance(driver))
            personalBook.updateMRBalance(mrAccounts['Pinecone'])
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
            presearchRewardsRedemptionAndBalanceUpdates(driver, bankAccounts['Presearch'], personalBook)
        elif "swagbucksMain" in request.POST:
            runSwagbucks(driver, True, mrAccounts['Swagbucks'], personalBook) if "Run Alu" in request.POST else runSwagbucks(driver, False, mrAccounts['Swagbucks'], personalBook)
        elif "swagbucksLogin" in request.POST:
            locateSwagBucksWindow(driver)
        elif "swagbucksAlu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif 'swagbucksBalance' in request.POST:
            mrAccounts['Swagbucks'].setBalance(getSwagBucksBalance(driver))
            personalBook.updateMRBalance(mrAccounts['Swagbucks'])
        elif "swagbucksContent" in request.POST:
            swagBuckscontentDiscovery(driver)
        elif "swabucksSearch" in request.POST:
            swagbucksSearch(driver)
        elif "swagbucksRewards" in request.POST:
            claimSwagBucksRewards(driver)
        elif "swagbucksInbox" in request.POST:
            swagbucksInbox(driver)
        elif "tellwutMain" in request.POST:
            runTellwut(driver, mrAccounts['Tellwut'], personalBook)
        elif "tellwutLogin" in request.POST:
            locateTellWutWindow(driver)
        elif "tellwutSurveys" in request.POST:
            completeTellWutSurveys(driver)            
        elif "tellwutBalance" in request.POST:
            mrAccounts['Tellwut'].setBalance(getTellWutBalance(driver))
            personalBook.updateMRBalance(mrAccounts['Tellwut'])            
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
            personalBook.overwriteBalance(mrAccounts['Paidviewpoint'])
        elif "paidviewpointRewards" in request.POST:
            redeemPaidviewpointRewards(driver)            
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))
    context = {'mrAccounts': mrAccounts, 'bankAccounts': bankAccounts, 'GME': "%.2f" % GME}
    personalBook.closeBook()
    jointBook.closeBook()
    if bankAccounts['Checking'].reviewTransactions or bankAccounts['Savings'].reviewTransactions:
        personalBook.openGnuCashUI()
    if bankAccounts['Ally'].reviewTransactions:
        jointBook.openGnuCashUI()
    return render(request,"scripts/daily.html", context)

def discover(request):
    book = GnuCash('Finance')
    Discover = USD("Discover", book)
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
    context = {'account': Discover}
    book.closeBook()
    return render(request,"scripts/discover.html", context)

def eternl(request):
    book = GnuCash('Finance')
    Cardano = Crypto("Cardano", book, 'ADA-Eternl')
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
    context = {'account': Cardano}
    book.closeBook()
    return render(request,"scripts/eternl.html", context)

def exodus(request):
    book = GnuCash('Finance')
    Cosmos = Crypto("Cosmos", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runExodus(Cosmos)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/exodus"))
    context = {'account': Cosmos}
    book.closeBook()
    return render(request,"scripts/exodus.html", context)

def fidelity(request):
    book = GnuCash('Finance')
    Fidelity = USD("Fidelity", book)    
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
    book.closeBook()
    return render(request,"scripts/fidelity.html", context)            
    
def healthEquity(request):
    book = GnuCash('Finance')
    HealthEquity = USD("HSA", book)
    Vanguard = USD("Vanguard401k", book)
    HEaccounts = {'HealthEquity': HealthEquity, 'Vanguard': Vanguard}
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
    context = {'HEaccounts': HEaccounts, 'HSA_dividends': HSA_dividends}
    book.closeBook()
    return render(request,"scripts/healthEquity.html", context)

def ioPay(request):
    book = GnuCash('Finance')
    IoTex = Crypto("IoTex", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runIoPay(driver, IoTex)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/iopay"))
    context = {'account': IoTex}
    book.closeBook()
    return render(request,"scripts/iopay.html", context)

def kraken(request):
    book = GnuCash('Finance')
    Ethereum2 = Crypto("Ethereum2", book)
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
    context = {'account': Ethereum2}
    book.closeBook()
    return render(request,"scripts/kraken.html", context)        

def ledger(request):
    book = GnuCash('Finance')
    coinList = getLedgerAccounts(book)
    if request.method == 'POST':
        if "main" in request.POST:
            runLedger(coinList)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/ledger"))
    context = {'coinList': coinList}
    book.closeBook()
    return render(request,"scripts/ledger.html", context)

def monthly(request):
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)
    HSA_dividends = ''
    if request.method == 'POST':
        driver = Driver("Chrome")
        today = datetime.today().date()
        if "USD" in request.POST:
            runUSD(driver, today, usdAccounts, personalBook)
        elif "prices" in request.POST:
            updateInvestmentPrices(driver, usdAccounts['Home'])
        elif "shares" in request.POST:
            healthEquity = getHealthEquityDividendsAndShares(driver, usdAccounts['HealthEquity'])
            vanguardInfo = getVanguardPriceAndShares(driver)
            fidelity = getFidelityShares(driver)
            updateInvestmentShares(driver, healthEquity, vanguardInfo, fidelity)
        elif "Crypto" in request.POST:
            runCrypto(driver, today, cryptoAccounts, personalBook)
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
            runCoinbase(driver, [cryptoAccounts['Loopring']], personalBook)
        elif "coinbaseLogin" in request.POST:
            locateCoinbaseWindow(driver)
        elif "coinbaseBalance" in request.POST:
            getCoinbaseBalances(driver, [cryptoAccounts['Loopring']])
        elif "eternlMain" in request.POST:
            runEternl(driver, cryptoAccounts['Cardano'], book)
        elif "eternlBalance" in request.POST:
            cryptoAccounts['Cardano'].setBalance(getEternlBalance(driver))
        elif "eternlLogin" in request.POST:
            locateEternlWindow(driver)
        elif "ioPayMain" in request.POST:
            runIoPay(driver, cryptoAccounts['IoTex'])
        elif "krakenMain" in request.POST:
            runKraken(driver, cryptoAccounts['Ethereum2'], personalBook)
        elif "krakenBalance" in request.POST:
            cryptoAccounts['Ethereum2'].setBalance(getKrakenBalance(driver))
        elif "krakenLogin" in request.POST:
            locateKrakenWindow(driver)
        elif "ledgerMain" in request.POST:
            runLedger(cryptoAccounts['ledgerAccounts'], personalBook)            
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/monthly"))
    context = {'usdAccounts': usdAccounts, 'cryptoAccounts': cryptoAccounts, 'HSA_dividends': HSA_dividends}
    personalBook.closeBook()
    jointBook.closeBook()
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
    book = GnuCash('Finance')
    Paidviewpoint = USD("Paidviewpoint", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPaidviewpoint(driver, Paidviewpoint, book)
        if "survey" in request.POST:
            completePaidviewpointSurvey(driver)
        elif "login" in request.POST:
            paidviewpointLogin(driver)        
        elif "balance" in request.POST:
            Paidviewpoint.setBalance(getPaidviewpointBalance(driver))
            Paidviewpoint.overwriteBalance(book)
        elif "rewards" in request.POST:
            redeemPaidviewpointRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paidviewpoint"))
    context = {'Paidviewpoint': Paidviewpoint}
    book.closeBook()
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
    book = GnuCash('Finance')
    Pinecone = Crypto("Pinecone", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runPinecone(driver, Pinecone, book)
        elif "login" in request.POST:
            locatePineconeWindow(driver)
        elif "balance" in request.POST:
            Pinecone.setBalance(getPineConeBalance(driver))
            book.updateMRBalance(Pinecone)
        elif "rewards" in request.POST:
            claimPineConeRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pinecone"))
    context = {'Pinecone': Pinecone}
    book.closeBook()
    return render(request,"scripts/pinecone.html", context)

def presearch(request):
    book = GnuCash('Finance')
    Presearch = Crypto("Presearch", book)
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
    context = {'account': Presearch}
    book.closeBook()
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
    book = GnuCash('Finance')
    Checking = USD("Sofi Checking", book)
    Savings = USD("Sofi Savings", book)
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
    context = {'Checking': Checking, 'Savings': Savings}
    book.closeBook()
    return render(request,"scripts/sofi.html", context)

def swagbucks(request):
    book = GnuCash('Finance')
    Swagbucks = Crypto("Swagbucks", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runSwagbucks(driver, True, Swagbucks, book) if "Run Alu" in request.POST else runSwagbucks(driver, False, Swagbucks, book)
        elif "login" in request.POST:
            locateSwagBucksWindow(driver)
        elif "alu" in request.POST:
            runAlusRevenge(driver.webDriver)
        elif 'balance' in request.POST:
            Swagbucks.setBalance(getSwagBucksBalance(driver))
            book.updateMRBalance(Swagbucks)            
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
    context = {'account': Swagbucks}
    book.closeBook()
    return render(request,"scripts/swagbucks.html", context)

def tellwut(request):
    book = GnuCash('Finance')
    Tellwut = Crypto("Tellwut", book)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            runTellwut(driver, Tellwut)
        elif "login" in request.POST:
            print(driver.webDriver.current_window_handle)
            locateTellWutWindow(driver)
        elif "surveys" in request.POST:
            completeTellWutSurveys(driver)
        elif "balance" in request.POST:
            Tellwut.setBalance(getTellWutBalance(driver))
            book.updateMRBalance(Tellwut)
        elif "rewards" in request.POST:
            redeemTellWutRewards(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/tellwut"))
    context = {'Tellwut': Tellwut}
    book.closeBook()
    return render(request,"scripts/tellwut.html", context)

def updateGoals(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()        
        if "main" in request.POST:
            account = body.get("accounts")
            timeframe = body.get("TimeFrame")
            book = GnuCash('Finance') if account == 'Personal' else GnuCash('Home')
            runUpdateGoals(account, timeframe, book)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/updateGoals"))      
    return render(request,"scripts/updateGoals.html")

def vanguard(request):
    book = GnuCash('Finance')
    Pension = USD("VanguardPension", book)
    V401k = USD("Vanguard401k", book)
    accounts = [Pension, V401k]
    pensionInterest = ""
    pensionContributions = ""
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:
            interestAndEmployerContribution = runVanguard(driver, accounts, book)
            pensionInterest = str(interestAndEmployerContribution['interest'])
            pensionContributions = str(interestAndEmployerContribution['employerContribution'])
        elif "login" in request.POST:
            locateVanguardWindow(driver)
        elif "balance" in request.POST:
            getVanguardBalanceAndInterestYTD(driver, accounts)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/vanguard"))
    context = {'Pension': Pension, 'PensionInterest': pensionInterest, 'PensionContributions': pensionContributions, 'V401k': V401k}
    book.closeBook()        
    return render(request,"scripts/vanguard.html", context)

def worthy(request):
    book = GnuCash('Finance')
    Worthy = USD("Worthy", book)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "balance" in request.POST:
            getWorthyBalance(driver, Worthy)
        elif "login" in request.POST:
            locateWorthyWindow(driver)
        elif "close windows" in request.POST:
            driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/worthy"))
    context = {'account': Worthy}
    book.closeBook()
    return render(request,"scripts/worthy.html", context)
