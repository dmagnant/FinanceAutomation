import os
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
from scripts.scripts.GamestopCC import *
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
from scripts.scripts.Webull import *
from scripts.scripts.Worthy import *
from scripts.scripts.Classes.WebDriver import Driver
from scripts.scripts.Classes.Asset import USD, Security
from scripts.scripts.Classes.WebDriverContext import WebDriverContext
from scripts.scripts.Classes.GnuCash import GnuCash
from scripts.scripts.Functions.GeneralFunctions import returnRender, getLogger
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from urllib.parse import urlencode
from django.template.loader import render_to_string
from requests.exceptions import ReadTimeout as ReadTimeoutError

def scripts(request):
    bank = ['Ally', 'Sofi', 'Fidelity', 'HealthEquity', 'Optum', 'Vanguard', 'Webull', 'Worthy']; bank.sort()
    cc = ['Amex', 'Barclays', 'BoA', 'Chase', 'Discover']; cc.sort();
    crypto = ['Coinbase', 'Eternl', 'IoPay', 'Ledger', 'Presearch']; crypto.sort()
    mr = ['AmazonGC', 'Bing', 'Paidviewpoint', 'Paypal', 'Pinecone', 'PSCoupons', 'Swagbucks', 'Tellwut']; mr.sort()
    if "close windows" in request.POST: driver = Driver("Chrome"); driver.closeWindowsExcept([':8000/'])
    context = {'bank':bank, 'cc':cc, 'crypto':crypto, 'mr':mr}
    return returnRender(request, "scripts.html", context)

def ally(request):
    book = GnuCash('Home')
    Ally = USD("Ally", book)
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:runAlly(driver, Ally, book, gnuCashTransactions, dateRange)
        elif "energy" in request.POST:  updateEnergyBillAmounts(driver, book, request.POST['energyTotal'])        
        elif "login" in request.POST:   locateAllyWindow(driver)
        elif "logout" in request.POST:  allyLogout(driver)
        elif "balance" in request.POST: Ally.setBalance(getAllyBalance(driver))
        elif "water" in request.POST:   payWaterBill(driver, book)
        elif "mortgage" in request.POST: mortgageBill(driver, book)
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
        elif "rewards" in request.POST:         claimAmexRewards(driver, Amex)
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
        elif "balance" in request.POST:         Bing.setBalance(getBingBalance(driver))
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
        elif "amexRewards" in request.POST:         claimAmexRewards(driver, Amex)
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
        elif "discoverRewards" in request.POST:     claimDiscoverRewards(driver, Discover)               
        elif "close windows" in request.POST:       driver.closeWindowsExcept([':8000/'])
    context = {'Amex': Amex, 'Barclays': Barclays, 'Chase': Chase, 'Discover': Discover, 'BoA_P': BoA_P, 'BoA_J': BoA_J}
    personalBook.closeBook();   jointBook.closeBook();    return returnRender(request, "banking/creditCards.html", context)

def dailyBank(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    bankAccounts = getDailyBankAccounts(personalBook, jointBook)
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = personalBook.getTransactionsByDateRange(dateRange)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "bank" in request.POST:              runDailyBank(bankAccounts, personalBook, jointBook, gnuCashTransactions, dateRange)
        elif "allyMain" in request.POST:        runAlly(driver, bankAccounts['Ally'], jointBook, gnuCashTransactions, dateRange)
        elif "allyLogin" in request.POST:       locateAllyWindow(driver)
        elif "allyLogout" in request.POST:      allyLogout(driver)        
        elif "allyBalance" in request.POST:     bankAccounts['Ally'].setBalance(getAllyBalance(driver))
        elif "paypal" in request.POST:          runPaypal(driver)
        elif "tearDown" in request.POST:        tearDown(driver)
        elif "paypalAdjust" in request.POST:    checkUncategorizedPaypalTransactions(driver, personalBook, bankAccounts['Paypal'], getStartAndEndOfDateRange(timeSpan=7))
        elif "sofiMain" in request.POST:        runSofi(driver, bankAccounts['Sofi'], personalBook, gnuCashTransactions, dateRange)
        elif "sofiLogin" in request.POST:       locateSofiWindow(driver)
        elif "sofiLogout" in request.POST:      sofiLogout(driver)
        elif "sofiBalances" in request.POST:    getSofiBalanceAndOrientPage(driver, bankAccounts['Sofi']['Checking']); getSofiBalanceAndOrientPage(driver, bankAccounts['Sofi']['Savings'])
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/']); driver.findWindowByUrl("scripts/daily")
    context = {'bankAccounts': bankAccounts}
    if bankAccounts['Sofi']['Checking'].reviewTransactions or bankAccounts['Sofi']['Savings'].reviewTransactions or bankAccounts['Paypal'].reviewTransactions:   personalBook.openGnuCashUI()
    if bankAccounts['Ally'].reviewTransactions:                                                                                                                  jointBook.openGnuCashUI()
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
        elif "pineconeBalance" in request.POST:         mrAccounts['Pinecone'].setBalance(getPineConeBalance(driver))
        elif "pineconeRewards" in request.POST:         claimPineConeRewards(driver)
        elif "presearchMain" in request.POST:           presearchRewardsRedemptionAndBalanceUpdates(driver, mrAccounts['Presearch'], personalBook)
        elif "presearchLogin" in request.POST:          locatePresearchWindow(driver)          
        elif "presearchBalance" in request.POST:        mrAccounts['Presearch'].setBalance(getPresearchBalance(driver))
        elif "presearchRewards" in request.POST:        presearchRewardsRedemptionAndBalanceUpdates(driver, mrAccounts['Presearch'], personalBook)
        elif "swagbucksMain" in request.POST:           runSwagbucks(driver, True, mrAccounts['Swagbucks'], personalBook) if "Run Alu" in request.POST else runSwagbucks(driver, False, mrAccounts['Swagbucks'], personalBook)
        elif "swagbucksLogin" in request.POST:          locateSwagBucksWindow(driver)
        elif "swagbucksAlu" in request.POST:            runAlusRevenge(driver)
        elif 'swagbucksBalance' in request.POST:        mrAccounts['Swagbucks'].setBalance(getSwagBucksBalance(driver))
        elif "swagbucksContent" in request.POST:        swagBuckscontentDiscovery(driver)
        elif "swabucksSearch" in request.POST:          swagbucksSearch(driver)
        elif "swagbucksRewards" in request.POST:        claimSwagBucksRewards(driver)
        elif "swagbucksInbox" in request.POST:          swagbucksInbox(driver)
        elif "tellwutMain" in request.POST:             runTellwut(driver, mrAccounts['Tellwut'], personalBook)
        elif "tellwutLogin" in request.POST:            locateTellWutWindow(driver)
        elif "tellwutSurveys" in request.POST:          completeTellWutSurveys(driver)            
        elif "tellwutBalance" in request.POST:          mrAccounts['Tellwut'].setBalance(getTellWutBalance(driver))            
        elif "tellwutRewards" in request.POST:          redeemTellWutRewards(driver)
        elif "paidviewpointMain" in request.POST:       runPaidviewpoint(driver, mrAccounts['Paidviewpoint'])
        elif "paidviewpointSurvey" in request.POST:     completePaidviewpointSurvey(driver)
        elif "paidviewpointLogin" in request.POST:      paidviewpointLogin(driver)        
        elif "paidviewpointBalance" in request.POST:    updatePaidViewPointBalance(driver, mrAccounts['Paidviewpoint'], personalBook)
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
        elif "rewards" in request.POST:         claimDiscoverRewards(driver, Discover)   
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
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange)
        elif "balance" in request.POST:         getFidelityBalance(driver, accounts)
        elif "login" in request.POST:           locateFidelityWindow(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/fidelity"))
    book.closeBook()
    context = {'accounts': accounts};   return returnRender(request, "banking/fidelity.html", context)

def gamestopCC(request):
    book = GnuCash('Finance')
    GamestopCC = USD("Gamestop CC", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runGamestopCC(driver, GamestopCC, book)
        elif "login" in request.POST:           locateGamestopCCWindow(driver)
        elif "balance" in request.POST:         GamestopCC.setBalance(getGamestopCCBalance(driver))
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/gamestopCC"))
    context = {'account': GamestopCC}
    book.closeBook();   return returnRender(request, "banking/creditcard.html", context)
  
def healthEquity(request):
    book = GnuCash('Finance')
    HEaccounts = getHealthEquityAccounts(book)
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runHealthEquity(driver, HEaccounts, book, gnuCashTransactions, lastMonth)
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
        Finances = Spreadsheet('Finances', 'Investments', driver)
        if "main" in request.POST:              runIoPay(driver, IoTex, book, Finances)
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
    book = GnuCash('Test')
    coinList = getLedgerAccounts(book)
    context = {}
    if request.method == 'POST':
        if "main" in request.POST:              runLedger(coinList)
        elif 'test' in request.POST:            
            return HttpResponseRedirect(reverse('Test'))
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/ledger"))
    context = {'coinList': coinList}
    book.closeBook();   return returnRender(request, "crypto/ledger.html", context)

def monthly(request):
    personalBook, jointBook = GnuCash('Finance'), GnuCash('Home')
    usdAccounts, cryptoAccounts = getMonthlyAccounts('USD', personalBook, jointBook), getMonthlyAccounts('Crypto', personalBook, jointBook)
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = personalBook.getTransactionsByDateRange(lastMonth)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "USD" in request.POST:                   runUSD(driver, usdAccounts, personalBook, gnuCashTransactions, lastMonth)
        elif "Crypto" in request.POST:              runCrypto(driver, cryptoAccounts, personalBook)
        elif "HEMain" in request.POST:              runHealthEquity(driver, usdAccounts['HealthEquity'], personalBook, gnuCashTransactions, lastMonth)
        elif "HELogin" in request.POST:             locateHealthEquityWindow(driver)
        elif "HEBalances" in request.POST:          getHealthEquityBalances(driver, usdAccounts['HealthEquity'])
        elif 'optumMain' in request.POST:           runOptum(driver, usdAccounts['Optum'], personalBook)    
        elif 'optumLogin' in request.POST:          locateOptumWindow(driver)
        elif 'optumBalance' in request.POST:        getOptumBalance(driver, usdAccounts['Optum'])
        elif "vanguard401k" in request.POST:        runVanguard401k(driver, usdAccounts['Vanguard'], personalBook)
        elif "vanguardLogin" in request.POST:       locateVanguardWindow(driver)
        elif "worthyBalance" in request.POST:       getWorthyBalance(driver, usdAccounts['Worthy'])
        elif "worthyLogin" in request.POST:         locateWorthyWindow(driver)
        elif "eternlMain" in request.POST:          runEternl(driver, cryptoAccounts['Cardano'], personalBook)
        elif "eternlBalance" in request.POST:       cryptoAccounts['Cardano'].setBalance(getEternlBalance(driver))
        elif "eternlLogin" in request.POST:         locateEternlWindow(driver)
        elif "ioPayMain" in request.POST:           runIoPay(driver, cryptoAccounts['IoTex'])
        elif "ledgerMain" in request.POST:          runLedger(cryptoAccounts['ledgerAccounts'], personalBook)          
        elif "Pension" in request.POST:             updatePensionBalanceAndCost(driver, personalBook, request.POST['newPensionBalance'])
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
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    OptumAccounts = {'VFIAX': VFIAX, 'OptumCash': OptumCash}
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runOptum(driver, OptumAccounts, book, gnuCashTransactions, lastMonth)
        elif "login" in request.POST:           locateOptumWindow(driver)
        elif "balance" in request.POST:         getOptumBalance(driver, OptumAccounts)
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
        elif "balance" in request.POST:         Pinecone.setBalance(getPineConeBalance(driver))
        elif "rewards" in request.POST:         claimPineConeRewards(driver)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/pinecone"))
    context = {'Pinecone': Pinecone}
    book.closeBook();   return returnRender(request, "mr/pinecone.html", context)

def presearch(request):
    book = GnuCash('Finance')
    Presearch = Security("Presearch", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        Finances = Spreadsheet('Finances', 'Investments', driver)
        if "main" in request.POST:              presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book, Finances)
        elif "login" in request.POST:           locatePresearchWindow(driver)          
        elif "balance" in request.POST:         Presearch.setBalance(getPresearchBalance(driver))
        elif "rewards" in request.POST:         presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book, Finances)
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
    accounts = getSofiAccounts(book)
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runSofi(driver, accounts, book, gnuCashTransactions, dateRange)
        elif "login" in request.POST:           locateSofiWindow(driver)
        elif "logout" in request.POST:          sofiLogout(driver)            
        elif "balances" in request.POST:        getSofiBalanceAndOrientPage(driver, accounts['Checking']);  getSofiBalanceAndOrientPage(driver, accounts['Savings'])
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/sofi"))
    context = {'Sofi':accounts}
    book.closeBook();   return returnRender(request, "banking/sofi.html", context)

def swagbucks(request):
    book = GnuCash('Finance')
    Swagbucks = Security("Swagbucks", book)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:                  runSwagbucks(driver, True, Swagbucks, book) if "Run Alu" in request.POST else runSwagbucks(driver, False, Swagbucks, book)
        elif "login" in request.POST:               locateSwagBucksWindow(driver)
        elif "alu" in request.POST:                 runAlusRevenge(driver)
        elif 'balance' in request.POST:             Swagbucks.setBalance(getSwagBucksBalance(driver))           
        elif "content" in request.POST:             swagBuckscontentDiscovery(driver)
        elif "search" in request.POST:              swagbucksSearch(driver)
        elif "rewards" in request.POST:             claimSwagBucksRewards(driver, Swagbucks)
        elif "inbox" in request.POST:               swagbucksInbox(driver)
        elif "close windows" in request.POST:       driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/swagbucks"))
    context = {'account': Swagbucks}
    book.closeBook();   return returnRender(request, "mr/swagbucks.html", context)

def tellwut(request, log=getLogger()):
    book = GnuCash('Finance')
    Tellwut = Security("Tellwut", book)
    if request.method == 'POST':
        print('post method received')
        with WebDriverContext("Chrome") as driver:
            if "main" in request.POST:
                print('running tellwut')
                runTellwut(driver, Tellwut, book)
            elif "login" in request.POST:
                locateTellWutWindow(driver)
            elif "surveys" in request.POST:
                completeTellWutSurveys(driver)
            elif "balance" in request.POST:
                Tellwut.setBalance(getTellWutBalance(driver))
            elif "rewards" in request.POST:
                Tellwut.setBalance(getTellWutBalance(driver))
                redeemTellWutRewards(driver, Tellwut)
            elif "close windows" in request.POST:
                driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/tellwut"))
        book.closeBook()
        # Include context data in the query parameters
        query_params = urlencode({'Tellwut': Tellwut})
        url = f"{reverse('Tellwut')}?{query_params}"
        return HttpResponseRedirect(url)  # Redirect to the same view with query parameters
        # return HttpResponseRedirect(reverse("Tellwut", args=(Tellwut,)))
    else:
        context = {'Tellwut': Tellwut}
        return returnRender(request, "mr/tellwut.html", context)
        # html = render_to_string("mr/tellwut.html", context)
        # # Create and return an HttpResponse object
        # return HttpResponse(html)

def updateGoals(request):
    context = {}
    if request.method == 'POST':
        driver, body = Driver("Chrome"), request.POST.copy()
        if "main" in request.POST:
            account = body.get("accounts")
            book = GnuCash('Finance') if account == 'Personal' else GnuCash('Home')
            context = runUpdateGoals(account, book)
            print(context)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/updateGoals"))
    return returnRender(request, "updateGoals.html", context)

def vanguard(request):
    book = GnuCash('Finance')
    accounts = getVanguardAccounts(book)
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "401k" in request.POST:              runVanguard401k(driver, accounts, book, gnuCashTransactions, lastMonth)
        elif "login" in request.POST:           locateVanguardWindow(driver)
        elif "balance" in request.POST:         getVanguardBalancesAndPensionInterestYTD(driver, accounts)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/vanguard"))
    context = {'accounts': accounts}
    book.closeBook();   return returnRender(request, "banking/vanguard.html", context)

def webull(request):
    book = GnuCash('Finance')
    accounts = getWebullAccounts(book)
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    if request.method == 'POST':
        driver = Driver("Chrome")
        if "main" in request.POST:              runWebullDaily(driver, accounts, book, gnuCashTransactions, dateRange)
        elif "login" in request.POST:           locateWebullWindow(driver)
        elif "balance" in request.POST:         getWebullBalance(driver, accounts)
        elif "close windows" in request.POST:   driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/webull"))
    context = {'accounts': accounts}
    book.closeBook();   return returnRender(request, "banking/webull.html", context)

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

def test(request):
    context = {'test': 'test'}
    if request.method == 'POST':
        driver = Driver("Chrome")
        # try:
        #     driver = Driver("Chrome")
        # except ReadTimeoutError as e:
        #     print(f"ReadTimeoutError: {e}")
        #     # Handle the timeout error, e.g., retry or log the error
        # except WebDriverException as e:
        #     print(f"WebDriverException: {e}")
        #     # Handle other WebDriver exceptions    
        print('driver steps done')
        # return HttpResponseRedirect(reverse('Ledger'))
        return returnRender(request, "crypto/ledger.html", context)
    return returnRender(request, "test.html", context)
