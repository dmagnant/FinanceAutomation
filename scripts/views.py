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
from scripts.scripts.DailyBank import *
from scripts.scripts.DailyMR import *
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
from scripts.scripts.Optum import *
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
from scripts.scripts.Classes.Asset import USD, Security
from scripts.scripts.Classes.GnuCash import GnuCash
from scripts.scripts.Functions.GeneralFunctions import returnRender

def scripts(request):
    bank = ['Ally', 'Sofi', 'Fidelity', 'HealthEquity', 'Optum', 'Vanguard', 'Worthy']; bank.sort()
    cc = ['Amex', 'Barclays', 'BoA', 'Chase', 'Discover']; cc.sort();
    crypto = ['Coinbase', 'Eternl', 'IoPay', 'Ledger', 'Presearch']; crypto.sort()
    mr = ['AmazonGC', 'Bing', 'Paidviewpoint', 'Paypal', 'Pinecone', 'PSCoupons', 'Swagbucks', 'Tellwut']; mr.sort()
    if "close windows" in request.POST: driver = Driver("Chrome"); driver.closeWindowsExcept([':8000/'])
    context = {'bank':bank, 'cc':cc, 'crypto':crypto, 'mr':mr}
    return returnRender(request, "scripts.html", context)

def ally(request):
    book = GnuCash('Home')
    Ally = USD("Ally", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:runAlly(driver, Ally, book)
        elif "energy" in request.POST:  updateEnergyBillAmounts(driver, book, request.POST['energyTotal'])        
        elif "login" in request.POST:   locateAllyWindow(driver)
        elif "logout" in request.POST:  allyLogout(driver)
        elif "balance" in request.POST: Ally.setBalance(getAllyBalance(driver))
        elif "water" in request.POST:   payWaterBill(driver, book)
    context = {'account': Ally}
    book.closeBook();   return returnRender(request, "banking/ally.html", context)

def amazon(request):
    book = GnuCash('Finance')
    AmazonGC = USD("Amazon GC", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              confirmAmazonGCBalance(driver, AmazonGC)
        elif 'earn' in request.POST or 'spend' in request.POST:
            requestInfo = request.POST.copy()
            del requestInfo['csrfmiddlewaretoken']
            writeAmazonGCTransactionFromUI(book, AmazonGC, requestInfo)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amazon"))
    context = {'account': AmazonGC}
    book.closeBook();   return returnRender(request, "mr/amazon.html", context)

def amex(request):
    book = GnuCash('Finance')
    Amex = USD("Amex", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runAmex(driver, Amex, book)
        elif "login" in request.POST:           locateAmexWindow(driver)
        elif "balance" in request.POST:         Amex.setBalance(getAmexBalance(driver))
        elif "rewards" in request.POST:         claimAmexRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/amex"))
    context = {'account': Amex}
    book.closeBook();   return returnRender(request, "banking/creditcard.html", context)

def barclays(request):
    book = GnuCash('Finance')
    Barclays = USD("Barclays", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runBarclays(driver, Barclays, book)
        elif "login" in request.POST:           locateBarclaysWindow(driver)
        elif "balance" in request.POST:         Barclays.setBalance(getBarclaysBalance(driver))
        elif "rewards" in request.POST:         claimBarclaysRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/barclays"))
    context = {'account': Barclays}
    book.closeBook();   return returnRender(request, "banking/creditcard.html", context)

def bing(request):
    book = GnuCash('Finance')
    Bing = Security("Bing", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runBing(driver, Bing, book)
        elif "login" in request.POST:           bingLogin(driver)
        elif "activities" in request.POST:      bingActivities(driver)
        elif "balance" in request.POST:         Bing.setBalance(getBingBalance(driver)); book.updateMRBalance(Bing)
        elif "rewards" in request.POST:         claimBingRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/bing"))
    context = {'Bing': Bing}
    book.closeBook();   return returnRender(request, "mr/bing.html", context)

def boa(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    Personal, Joint = USD("BoA", personalBook), USD("BoA-joint", jointBook)
    if request.method == 'POST':
        driver, account = Driver("Chrome"), request.POST.copy().get("account")
        if "main" in request.POST:              runBoA(driver, Personal, personalBook) if account == 'Personal' else runBoA(driver, Joint, jointBook)
        elif "login" in request.POST:           locateBoAWindowAndOpenAccount(driver, account)
        elif "balance" in request.POST:         Personal.setBalance(getBoABalance(driver, account)) if account == 'Personal' else Joint.setBalance(getBoABalance(driver, account))
        elif "rewards" in request.POST:         claimBoARewards(driver, account)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/boa"))
    context = {'Personal': Personal, 'Joint': Joint}
    personalBook.closeBook(); jointBook.closeBook();    return returnRender(request, "banking/boa.html", context)

def chase(request):
    book = GnuCash('Finance')
    Chase = USD("Chase", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runChase(driver, Chase, book)
        elif "login" in request.POST:           locateChaseWindow(driver)
        elif "balance" in request.POST:         Chase.setBalance(getChaseBalance(driver))
        elif "rewards" in request.POST:         claimChaseRewards(driver)   
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/chase"))
    context = {'account': Chase}
    book.closeBook();   return returnRender(request, "banking/creditcard.html", context)

def coinbase(request):
    book = GnuCash('Finance')
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runCoinbase(driver, book)
        elif "login" in request.POST:           locateCoinbaseWindow(driver)
        elif "balance" in request.POST:         getCoinbaseBalances(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/coinbase"))      
    context = {}
    book.closeBook();   return returnRender(request, "crypto/coinbase.html", context)

def creditCards(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    Amex, Barclays, Chase, Discover, BoA_P, BoA_J = USD("Amex", personalBook), USD("Barclays", personalBook), USD("Chase", personalBook), USD("Discover", personalBook), USD("BoA", personalBook), USD("BoA-joint", jointBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "amexMain" in request.POST:              runAmex(driver, Amex, personalBook)
        elif "amexLogin" in request.POST:           locateAmexWindow(driver)
        elif "amexBalances" in request.POST:        Amex.setBalance(getAmexBalance(driver))
        elif "amexRewards" in request.POST:         claimAmexRewards(driver)
        elif "barclaysMain" in request.POST:        runBarclays(driver, Barclays, personalBook)
        elif "barclaysLogin" in request.POST:       locateBarclaysWindow(driver)
        elif "barclaysBalances" in request.POST:    Barclays.setBalance(getBarclaysBalance(driver))
        elif "barclaysRewards" in request.POST:     claimBarclaysRewards(driver)
        elif "boaPMain" in request.POST:            runBoA(driver, BoA_P, personalBook)
        elif "boaPLogin" in request.POST:           locateBoAWindowAndOpenAccount(driver, BoA_P.name)
        elif "boaPBalances" in request.POST:        BoA_P.setBalance(getBoABalance(driver, BoA_P.name))
        elif "boaPRewards" in request.POST:         claimBoARewards(driver, BoA_P.name)
        elif "boaJMain" in request.POST:            runBoA(driver, BoA_J, jointBook)
        elif "boaJLogin" in request.POST:           locateBoAWindowAndOpenAccount(driver, BoA_J.name)
        elif "boaJBalances" in request.POST:        BoA_J.setBalance(getBoABalance(driver, BoA_J.name))
        elif "boaJRewards" in request.POST:         claimBoARewards(driver, BoA_J.name)
        elif "chaseMain" in request.POST:           runChase(driver, Chase, personalBook)
        elif "chaseLogin" in request.POST:          locateChaseWindow(driver)
        elif "chaseBalances" in request.POST:       Chase.setBalance(getChaseBalance(driver))
        elif "chaseRewards" in request.POST:        claimChaseRewards(driver)
        elif "discoverMain" in request.POST:        runDiscover(driver, Discover, personalBook)
        elif "discoverLogin" in request.POST:       locateDiscoverWindow(driver)
        elif "discoverBalances" in request.POST:    Discover.setBalance(getDiscoverBalance(driver))
        elif "discoverRewards" in request.POST:     claimDiscoverRewards(driver)               
        elif "close windows" in request.POST:       driver.closeWindowsExcept([':8000/'])
    context = {'Amex': Amex, 'Barclays': Barclays, 'Chase': Chase, 'Discover': Discover, 'BoA_P': BoA_P, 'BoA_J': BoA_J}
    personalBook.closeBook();   jointBook.closeBook();    return returnRender(request, "banking/creditCards.html", context)

def dailyBank(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    bankAccounts, GME = getDailyBankAccounts(personalBook, jointBook), personalBook.getPriceInGnucash('GME', datetime.today().date())
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "bank" in request.POST:GME =         runDailyBank(bankAccounts, personalBook, jointBook)
        elif "allyMain" in request.POST:        runAlly(driver, bankAccounts['Ally'], jointBook)
        elif "allyLogin" in request.POST:       locateAllyWindow(driver)
        elif "allyLogout" in request.POST:      allyLogout(driver)        
        elif "allyBalance" in request.POST:     bankAccounts['Ally'].setBalance(getAllyBalance(driver))
        elif "paypal" in request.POST:          runPaypal(driver)
        elif "tearDown" in request.POST:        tearDown(driver)
        elif "paypalAdjust" in request.POST:    checkUncategorizedPaypalTransactions(driver, personalBook, bankAccounts['Paypal'], getStartAndEndOfDateRange(timeSpan=7))
        elif "sofiMain" in request.POST:        runSofi(driver, accounts)
        elif "sofiLogin" in request.POST:       locateSofiWindow(driver)
        elif "sofiLogout" in request.POST:      sofiLogout(driver)
        elif "sofiBalances" in request.POST:    getSofiBalanceAndOrientPage(driver, bankAccounts['Checking']); getSofiBalanceAndOrientPage(driver, bankAccounts['Savings'])
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/']); driver.findWindowByUrl("scripts/daily")
    context = {'bankAccounts': bankAccounts, 'GME': "%.2f" % GME}
    if bankAccounts['Checking'].reviewTransactions or bankAccounts['Savings'].reviewTransactions or bankAccounts['Paypal'].reviewTransactions:   personalBook.openGnuCashUI()
    if bankAccounts['Ally'].reviewTransactions:                                                     jointBook.openGnuCashUI()
    personalBook.closeBook();   jointBook.closeBook();    return returnRender(request, "banking/dailyBank.html", context)

def dailyMR(request):
    personalBook = GnuCash('Finance')
    mrAccounts = getDailyMRAccounts(personalBook)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "MR" in request.POST:                        runDailyMR(mrAccounts, personalBook)
        elif "amazonMain" in request.POST:              confirmAmazonGCBalance(driver, mrAccounts['AmazonGC'])
        elif "pineconeMain" in request.POST:            runPinecone(driver, mrAccounts['Pinecone'], personalBook)
        elif "pineconeLogin" in request.POST:           locatePineconeWindow(driver)
        elif "pineconeBalance" in request.POST:         mrAccounts['Pinecone'].setBalance(getPineConeBalance(driver));  personalBook.updateMRBalance(mrAccounts['Pinecone'])
        elif "pineconeRewards" in request.POST:         claimPineConeRewards(driver)
        elif "presearchMain" in request.POST:           presearchRewardsRedemptionAndBalanceUpdates(driver, mrAccounts['Presearch'], personalBook)
        elif "presearchLogin" in request.POST:          locatePresearchWindow(driver)          
        elif "presearchBalance" in request.POST:        mrAccounts['Presearch'].setBalance(getPresearchBalance(driver))
        elif "presearchRewards" in request.POST:        presearchRewardsRedemptionAndBalanceUpdates(driver, mrAccounts['Presearch'], personalBook)
        elif "swagbucksMain" in request.POST:           runSwagbucks(driver, True, mrAccounts['Swagbucks'], personalBook) if "Run Alu" in request.POST else runSwagbucks(driver, False, mrAccounts['Swagbucks'], personalBook)
        elif "swagbucksLogin" in request.POST:          locateSwagBucksWindow(driver)
        elif "swagbucksAlu" in request.POST:            runAlusRevenge(driver.webDriver)
        elif 'swagbucksBalance' in request.POST:        mrAccounts['Swagbucks'].setBalance(getSwagBucksBalance(driver));    personalBook.updateMRBalance(mrAccounts['Swagbucks'])
        elif "swagbucksContent" in request.POST:        swagBuckscontentDiscovery(driver)
        elif "swabucksSearch" in request.POST:          swagbucksSearch(driver)
        elif "swagbucksRewards" in request.POST:        claimSwagBucksRewards(driver)
        elif "swagbucksInbox" in request.POST:          swagbucksInbox(driver)
        elif "tellwutMain" in request.POST:             runTellwut(driver, mrAccounts['Tellwut'], personalBook)
        elif "tellwutLogin" in request.POST:            locateTellWutWindow(driver)
        elif "tellwutSurveys" in request.POST:          completeTellWutSurveys(driver)            
        elif "tellwutBalance" in request.POST:          mrAccounts['Tellwut'].setBalance(getTellWutBalance(driver));    personalBook.updateMRBalance(mrAccounts['Tellwut'])            
        elif "tellwutRewards" in request.POST:          redeemTellWutRewards(driver)
        elif "paidviewpointMain" in request.POST:       runPaidviewpoint(driver, mrAccounts['Paidviewpoint'])
        elif "paidviewpointSurvey" in request.POST:     completePaidviewpointSurvey(driver)
        elif "paidviewpointLogin" in request.POST:      paidviewpointLogin(driver)        
        elif "paidviewpointBalance" in request.POST:    mrAccounts['Paidviewpoint'].setBalance(getPaidviewpointBalance(driver));    personalBook.overwriteBalance(mrAccounts['Paidviewpoint'])
        elif "paidviewpointRewards" in request.POST:    redeemPaidviewpointRewards(driver)            
        elif "close windows" in request.POST:           driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/dailyMR"))
    context = {'mrAccounts': mrAccounts}
    personalBook.closeBook();   return returnRender(request, "mr/dailyMR.html", context)
        
def discover(request):
    book = GnuCash('Finance')
    Discover = USD("Discover", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runDiscover(driver, Discover, book)
        elif "login" in request.POST:           locateDiscoverWindow(driver)
        elif "balance" in request.POST:         Discover.setBalance(getDiscoverBalance(driver))
        elif "rewards" in request.POST:         claimDiscoverRewards(driver)   
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/discover"))
    context = {'account': Discover}
    book.closeBook();   return returnRender(request, "banking/creditcard.html", context)

def eternl(request):
    book = GnuCash('Finance')
    Cardano = Security("Cardano", book, 'ADA-Eternl')
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runEternl(driver, Cardano, book)
        elif "balance" in request.POST:         Cardano.setBalance(getEternlBalance(driver))
        elif "login" in request.POST:           locateEternlWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/eternl"))
    context = {'account': Cardano}
    book.closeBook();   return returnRender(request, "crypto/eternl.html", context)

def exodus(request):
    book = GnuCash('Finance')
    Cosmos = Security("Cosmos", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runExodus(Cosmos)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/exodus"))
    context = {'account': Cosmos}
    book.closeBook();   return returnRender(request, "crypto/exodus.html", context)

def fidelity(request):
    book = GnuCash('Finance')
    accounts = getFidelityAccounts(book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runFidelity(driver, accounts, book)
        elif "balance" in request.POST:         getFidelityBalance(driver, accounts)
        elif "login" in request.POST:           locateFidelityWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/fidelity"))
    book.closeBook()
    context = {'accounts': accounts};   return returnRender(request, "banking/fidelity.html", context)
    
def healthEquity(request):
    book = GnuCash('Finance')
    VIIIX, HECash, V401k = Security("HE Investment", book), USD("HE Cash", book), USD("Vanguard401k", book)
    HEaccounts = {'VIIIX': VIIIX, 'HECash': HECash, 'V401k': V401k}
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runHealthEquity(driver, HEaccounts)
        elif "login" in request.POST:           locateHealthEquityWindow(driver)
        elif "balance" in request.POST:         getHealthEquityBalances(driver, HEaccounts)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/healthEquity"))
    context = {'HEaccounts': HEaccounts}
    book.closeBook();   return returnRender(request, "banking/healthEquity.html", context)

def ioPay(request):
    book = GnuCash('Finance')
    IoTex = Security("IoTex", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runIoPay(driver, IoTex, book)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/iopay"))
    context = {'account': IoTex}
    book.closeBook();   return returnRender(request, "crypto/iopay.html", context)

def kraken(request):
    book = GnuCash('Finance')
    Ethereum2 = Security("Ethereum2", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runKraken(driver, Ethereum2)
        elif "balance" in request.POST:         Ethereum2.setBalance(getKrakenBalance(driver))
        elif "login" in request.POST:           locateKrakenWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/kraken"))
    context = {'account': Ethereum2}
    book.closeBook();   return returnRender(request, "crypto/kraken.html", context)

def ledger(request):
    book = GnuCash('Finance')
    coinList = getLedgerAccounts(book)
    if request.method == 'POST':
        if "main" in request.POST:              runLedger(coinList)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/ledger"))
    context = {'coinList': coinList}
    book.closeBook();   return returnRender(request, "crypto/ledger.html", context)

def monthly(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    usdAccounts, cryptoAccounts = getMonthlyAccounts('USD', personalBook, jointBook), getMonthlyAccounts('Crypto', personalBook, jointBook)
    if request.method == 'POST':
        driver, today = Driver("Chrome"), datetime.today().date()
        if "USD" in request.POST:                   runUSD(driver, today, usdAccounts, personalBook)
        elif "Crypto" in request.POST:              runCrypto(driver, cryptoAccounts, personalBook)
        elif "fidelityMain" in request.POST:        runFidelity(driver, usdAccounts, personalBook)
        elif "fidelityBalance" in request.POST:     getFidelityBalance(driver, accounts)
        elif "fidelityLogin" in request.POST:       locateFidelityWindow(driver)
        elif "HEMain" in request.POST:              runHealthEquity(driver, {'VIIIX': usdAccounts['VIIIX'], 'HECash': usdAccounts['HECash'], 'V401k': usdAccounts['V401k']}, personalBook)
        elif "HELogin" in request.POST:             locateHealthEquityWindow(driver)
        elif "HEBalances" in request.POST:          getHealthEquityBalances(driver, {'VIIIX': usdAccounts['VIIIX'], 'HECash': usdAccounts['HECash'], 'V401k': usdAccounts['V401k']})
        elif "vanguard401k" in request.POST:        runVanguard401k(driver, usdAccounts, personalBook)
        elif "vanguardLogin" in request.POST:       locateVanguardWindow(driver)
        elif "vanguardBalances" in request.POST:    getVanguardBalancesAndPensionInterestYTD(driver, [usdAccounts['Pension'], usdAccounts['V401k']])
        elif "worthyBalance" in request.POST:       getWorthyBalance(driver, usdAccounts['Worthy'])
        elif "worthyLogin" in request.POST:         locateWorthyWindow(driver)
        elif "eternlMain" in request.POST:          runEternl(driver, cryptoAccounts['Cardano'], personalBook)
        elif "eternlBalance" in request.POST:       cryptoAccounts['Cardano'].setBalance(getEternlBalance(driver))
        elif "eternlLogin" in request.POST:         locateEternlWindow(driver)
        elif "ioPayMain" in request.POST:           runIoPay(driver, cryptoAccounts['IoTex'])
        elif "krakenMain" in request.POST:          runKraken(driver, cryptoAccounts['Ethereum2'], personalBook)
        elif "krakenBalance" in request.POST:       cryptoAccounts['Ethereum2'].setBalance(getKrakenBalance(driver))
        elif "krakenLogin" in request.POST:         locateKrakenWindow(driver)
        elif "ledgerMain" in request.POST:          runLedger(cryptoAccounts['ledgerAccounts'], personalBook)            
        elif "close windows" in request.POST:       driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/monthly"))
    context = {'usdAccounts': usdAccounts, 'cryptoAccounts': cryptoAccounts}
    personalBook.closeBook();   jointBook.closeBook();    return returnRender(request, "monthly.html", context)

def myConstant(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        body = request.POST.copy()
        if "main" in request.POST or "balance" in request.POST:
            currency = body.get("type")
            response = runMyConstant(driver, currency) if "main" in request.POST else getMyConstantBalances(driver, currency)
            if currency == "USD":               response.getData()
            elif currency == "Crypto":
                for coin in response:           coin.getData()
        elif "login" in request.POST:           locateMyConstantWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/myConstant"))
    return render(request,"banking/myconstant.html")

def optum(request):
    book = GnuCash('Finance')
    VFIAX, OptumCash = Security("VFIAX", book), USD("Optum Cash", book)
    OptumAccounts = {'VFIAX': VFIAX, 'OptumCash': OptumCash}
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runOptum(driver, OptumAccounts, book)
        elif "login" in request.POST:           locateOptumWindow(driver)
        elif "balance" in request.POST:         getOptumBalance(driver, OptumAccounts, book)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/optum"))
    context = {'OptumAccounts': OptumAccounts}
    book.closeBook();   return returnRender(request, "banking/optum.html", context)

def paidviewpoint(request):
    book = GnuCash('Finance')
    Paidviewpoint = USD("Paidviewpoint", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runPaidviewpoint(driver, Paidviewpoint, book)
        if "survey" in request.POST:            completePaidviewpointSurvey(driver)
        elif "login" in request.POST:           paidviewpointLogin(driver)        
        elif "balance" in request.POST:         Paidviewpoint.setBalance(getPaidviewpointBalance(driver))
        elif "rewards" in request.POST:         redeemPaidviewpointRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paidviewpoint"))
    context = {'Paidviewpoint': Paidviewpoint}
    book.closeBook();   return returnRender(request, "mr/paidviewpoint.html", context)

def paypal(request):
    if request.method == 'POST':            driver = Driver("Chrome")
    if "main" in request.POST:              runPaypal(driver)
    elif "login" in request.POST:           locatePayPalWindow(driver)
    elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/paypal"))        
    return render(request,"mr/paypal.html")

def pinecone(request):
    book = GnuCash('Finance')
    Pinecone = Security("Pinecone", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runPinecone(driver, Pinecone, book)
        elif "login" in request.POST:           locatePineconeWindow(driver)
        elif "balance" in request.POST:         Pinecone.setBalance(getPineConeBalance(driver));book.updateMRBalance(Pinecone)
        elif "rewards" in request.POST:         claimPineConeRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pinecone"))
    context = {'Pinecone': Pinecone}
    book.closeBook();   return returnRender(request, "mr/pinecone.html", context)

def presearch(request):
    book = GnuCash('Finance')
    Presearch = Security("Presearch", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book)
        elif "login" in request.POST:           locatePresearchWindow(driver)          
        elif "balance" in request.POST:         Presearch.setBalance(getPresearchBalance(driver))
        elif "rewards" in request.POST:         presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/presearch"))
    context = {'account': Presearch}
    book.closeBook();   return returnRender(request, "crypto/presearch.html", context)

def psCoupons(request):
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runPSCoupon(driver)
        elif "login" in request.POST:           locatePSCouponWindow(driver)         
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pscoupons"))             
    return render(request,"mr/pscoupons.html")

def sofi(request):
    book = GnuCash('Finance')
    Checking, Savings = USD("Sofi Checking", book), USD("Sofi Savings", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runSofi(driver, [Checking, Savings], book)
        elif "login" in request.POST:           locateSofiWindow(driver)
        elif "logout" in request.POST:          sofiLogout(driver)            
        elif "balances" in request.POST:        getSofiBalanceAndOrientPage(driver, Checking);  getSofiBalanceAndOrientPage(driver, Savings)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/sofi"))
    context = {'Checking': Checking, 'Savings': Savings}
    book.closeBook();   return returnRender(request, "banking/sofi.html", context)

def swagbucks(request):
    book = GnuCash('Finance')
    Swagbucks = Security("Swagbucks", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:                  runSwagbucks(driver, True, Swagbucks, book) if "Run Alu" in request.POST else runSwagbucks(driver, False, Swagbucks, book)
        elif "login" in request.POST:               locateSwagBucksWindow(driver)
        elif "alu" in request.POST:                 runAlusRevenge(driver.webDriver)
        elif 'balance' in request.POST:             Swagbucks.setBalance(getSwagBucksBalance(driver));  book.updateMRBalance(Swagbucks)            
        elif "content" in request.POST:             swagBuckscontentDiscovery(driver)
        elif "search" in request.POST:              swagbucksSearch(driver)
        elif "rewards" in request.POST:             claimSwagBucksRewards(driver)
        elif "inbox" in request.POST:               swagbucksInbox(driver)
        elif "close windows" in request.POST:       driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/swagbucks"))
    context = {'account': Swagbucks}
    book.closeBook();   return returnRender(request, "mr/swagbucks.html", context)

def tellwut(request):
    book = GnuCash('Finance')
    Tellwut = Security("Tellwut", book)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runTellwut(driver, Tellwut, book)
        elif "login" in request.POST:           locateTellWutWindow(driver)
        elif "surveys" in request.POST:         completeTellWutSurveys(driver)
        elif "balance" in request.POST:         Tellwut.setBalance(getTellWutBalance(driver));  book.updateMRBalance(Tellwut)
        elif "rewards" in request.POST:         redeemTellWutRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/tellwut"))
    context = {'Tellwut': Tellwut}
    book.closeBook();   return returnRender(request, "mr/tellwut.html", context)

def updateGoals(request):
    context = {}
    if request.method == 'POST':
        driver, body = Driver("Chrome"), request.POST.copy()
        if "main" in request.POST:
            account, timeFrame = body.get("accounts"), body.get("TimeFrame")
            book = GnuCash('Finance') if account == 'Personal' else GnuCash('Home')
            context = runUpdateGoals(account, timeFrame, book)
            print(context)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/updateGoals"))
    return returnRender(request, "updateGoals.html", context)

def vanguard(request):
    book = GnuCash('Finance')
    Pension, V401k, TSM401k, EBI = USD("VanguardPension", book), USD("Vanguard401k", book), Security("Total Stock Market(401k)", book), Security("Employee Benefit Index", book)
    accounts = {'Pension': Pension, 'V401k': V401k,'TSM401k': TSM401k,'EBI':EBI}
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "401k" in request.POST:              runVanguard401k(driver, accounts, book)
        elif "Pension" in request.POST:         runVanguardPension(driver, accounts, book)
        elif "login" in request.POST:           locateVanguardWindow(driver)
        elif "balance" in request.POST:         getVanguardBalancesAndPensionInterestYTD(driver, accounts)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/vanguard"))
    context = {'accounts': accounts}
    book.closeBook();   return returnRender(request, "banking/vanguard.html", context)

def worthy(request):
    book = GnuCash('Finance')
    Worthy = USD("Worthy", book)    
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "balance" in request.POST:           getWorthyBalance(driver, Worthy)
        elif "login" in request.POST:           locateWorthyWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/worthy"))
    context = {'account': Worthy}
    book.closeBook();   return returnRender(request, "banking/worthy.html", context)
