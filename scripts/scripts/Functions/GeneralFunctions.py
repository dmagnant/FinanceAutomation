import ctypes
import os
import time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.shortcuts import render
from datetime import datetime


import psutil
import pyotp
from pycoingecko import CoinGeckoAPI
from pykeepass import PyKeePass
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException, WebDriverException)
from selenium.webdriver.common.by import By

def showMessage(header, body): 
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, body, header, 0)
    
def setDirectory():
    return os.environ.get('StorageDirectory')    

def isProcessRunning(processName):
    for proc in psutil.process_iter():
        if (proc.name().lower()==processName):
            print(processName)
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def getUsername(name):
    keepass_file = setDirectory() + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).username

def getPassword(name):
    keepass_file = setDirectory() + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).password

def getOTP(account):
    return pyotp.TOTP(os.environ.get(account)).now()

def loginPiHole(driver):
    driver.implicitly_wait(2)
    driver.get("http://192.168.1.144/admin/")
    driver.maximize_window()
    try:
        driver.find_element(By.XPATH, "/html/body/div[2]/aside/section/ul/li[3]/a").click() # login
        driver.find_element(By.ID, "loginpw").send_keys(getPassword('Pi hole'))
        driver.find_element(By.XPATH, "//*[@id='loginform']/div[2]/div/button").click() # login
        time.sleep(1)
    except NoSuchElementException:
        exception = "already logged in"

def disablePiHole(driver):
    driver.maximize_window()
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(driver)
    try:
        driver.find_element(By.XPATH, "//*[@id='pihole-disable']/a/span[2]").click()
        driver.find_element(By.XPATH, "//*[@id='pihole-disable-indefinitely']").click() # indefinitely 
    except ElementNotInteractableException:
        exception = "already disabled"

def enablePiHole(driver):
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(driver)
    try:
        driver.find_element(By.ID, "enableLabel").click()
    except NoSuchElementException:
        exception = "already enabled"
    except ElementNotInteractableException:
        exception = "already enabled"

def getStartAndEndOfDateRange(today, timeSpan):
    month = today.month
    year = today.year
    if isinstance(timeSpan, int):
        endDate = today
        startDate = (endDate - timedelta(days=timeSpan))
    else:
        if month == 1:
            startDate = today.replace(month=12, day=1, year=year - 1)
            endDate = today.replace(month=12, day=31, year=year - 1)
        elif month == 3:
            startDate = today.replace(month=2, day=1)
            endDate = today.replace(month=2, day=28) if (year % 4)>0 else today.replace(month=2,day=29)
        elif month in [5, 7, 10, 12]:
            startDate = today.replace(month=month - 1, day=1)
            endDate = today.replace(month=month - 1, day=30)
        else:
            startDate = today.replace(month=month - 1, day=1)
            endDate = today.replace(month=month - 1, day=31)
        if timeSpan == "YTD":
            startDate = startDate.replace(month=1, day=1)
    return {
        'startDate': startDate,
        'endDate': endDate
    }

def getCryptocurrencyPrice(coinList):
    return CoinGeckoAPI().get_price(ids=coinList, vs_currencies='usd')
     
def getStockPrice(driver, symbol):
    driver.openNewWindow('https://finance.yahoo.com/quote/' + symbol + "/")
    driver.webDriver.implicitly_wait(1)
    try:
        driver.webDriver.find_element(By.XPATH,"//*[@id='myLightboxContainer']/section/button[1]/svg").click()
    except NoSuchElementException:
        exception = 'pop-up window not there'
    price = float(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div/fin-streamer[1]").text.replace('$', ''))
    try:
        driver.webDriver.close()
    except WebDriverException:
        print(WebDriverException)
    driver.switchToLastWindow()
    driver.webDriver.implicitly_wait(3)
    return round(Decimal(price), 2)

def modifyTransactionDescription(description, amount="0.00"):
    if "SAVINGS ACCOUNT XXXXXX9703" in description.upper():
        description = "Tessa Deposit"
    elif "INTEREST EARNED" in description.upper() or "SOFI REWARDS REDEMPTION" in description.upper() or "Interest for " in description:
        description = "Interest Earned"
    elif "VIIIX: Buy" in description:
        description = "HSA Investment"
    elif "VIIIX: Dividend" in description:
        description = "HSA Dividend"
    elif "Employer Contribution" in description:
        description = 'HSA Employer Contribution'
    elif "Plan Contribution" in description:
        description = "401k Investment"
    elif "Dividends on Equity Investments" in description:
        description = "401k Dividend"
    elif "DIVIDEND RECEIVED" in description:
        description = "IRA Dividend"
    elif "YOU BOUGHT" in description:
        description = "IRA Investment"
    elif "YOU SOLD" in description:
        description = "IRA sale of stock"
    elif "Fee Real Estate" in description or "Fee Instl Tot Stk" in description:
        description = "401k Fee"
    elif "JONATHON MAGNANT" in description.upper():
        description = "Jonny payment"
    elif "SAVINGS - 3467" in description.upper():
        description = "Savings Transfer"
    elif "ALLY BANK TRANSFER" in description.upper():
        description = "Dan Deposit"
    elif "ALLY BANK" in description.upper():
        description = "Ally Transfer"
    elif "FID BKG SVC LLC" in description.upper():
        description = "Fidelity Transfer"
    elif "CITY OF MILWAUKE B2P*MILWWA" in description.upper():
        description = "Water Bill"
    elif "COOPER NSM" in description.upper():
        description = "Mortgage Payment"
    elif "NORTHWESTERN MUT" in description.upper():
        description = "NM Paycheck"
    elif "STATE FARM COS" in description.upper():
        description = "SF Paycheck"        
    elif "PAYPAL" in description.upper() and "10.00" in amount:
        description = "Swagbucks"
    elif "PAYPAL" in description.upper() and amount == "3.00":
        description = "Pinecone"
    elif "PAYPAL" in description.upper():
        description = "Paypal"
    elif "VENMO" in description.upper():
        description = "Venmo"
    elif "ALLIANT CU" in description.upper():
        description = "Alliant Transfer"        
    elif "AMEX EPAYMENT" in description.upper():
        description = "Amex CC"
    elif "YOUR CASH REWARD/REFUND IS" in description.upper():
        description = "Amex CC Rewards"
    elif "SPECTRUM" in description.upper():
        description = "Internet Bill"
    elif "COINBASE" in description.upper():
        description = "Crypto purchase"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) > 0:
        description = "Chase CC Rewards"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) < 0:
        description = "Chase CC"
    elif "AUTOMATIC STATEMENT CREDIT" in description.upper():
        description = "Discover CC Rewards"        
    elif "DISCOVER" in description.upper():
        description = "Discover CC"
    elif "BARCLAYCARD US" in description.upper() and float(amount) > 0:
        description = "Barclays CC Rewards"
    elif "BARCLAYCARD US" in description.upper() and float(amount) < 0:
        description = "Barclays CC"        
    elif "BK OF AMER VISA" in description.upper():
        description = "BoA CC"
    elif "CASH REWARDS STATEMENT CREDIT" in description.upper():
        description = "BoA CC Rewards"
    return description

def getAccountPath(account):
    if account.account != None:
        accountName = account.account
    else:
        accountName = account.name
    assets = "Assets"
    liquid = assets + ":Liquid Assets"
    mr = liquid + ":MR"    
    nonLiquid = assets + ":Non-Liquid Assets"
    crypto = nonLiquid + ":CryptoCurrency"
    v401k = nonLiquid + ":401k"
    ira = nonLiquid + ":IRA"
    hsa = nonLiquid + ":HSA"
    liabilities = "Liabilities"
    cc = liabilities + ":Credit Cards"
    bonds = liabilities + ":Bonds"
    match accountName:
        case 'Crypto':
            return crypto
        case 'Cardano':
            return crypto + ":" + accountName
        case 'ADA-Eternl':
            return crypto + ":Cardano:" + accountName
        case 'ADA-Nami':
            return crypto + ":Cardano:" + accountName
        case 'Algorand':
            return crypto + ":" + accountName
        case 'Cosmos':
            return crypto + ":" + accountName
        case 'Bitcoin':
            return crypto + ":" + accountName
        case 'Polkadot':
            return crypto + ":" + accountName
        case 'Ethereum':
            return crypto + ":" + accountName
        case 'IoTex':
            return crypto + ":" + accountName
        case 'Presearch':
            return crypto + ":" + accountName
        case 'Ripple':
            return crypto + ":" + accountName
        case 'Loopring':
            return crypto + ":" + accountName
        case 'Amex':
            return cc + ":" + "Amex BlueCash Everyday"
        case 'Barclays':
            return cc + ":" + "BarclayCard CashForward"
        case 'BoA':
            return cc + ":" + "BankAmericard Cash Rewards"
        case 'Chase':
            return cc + ":" + "Chase Freedom"
        case 'Discover':
            return cc + ":" + "Discover It"
        case 'Liquid Assets':
            return liquid
        case 'Amazon GC':
            return liquid + ":" + accountName
        case 'Sofi Checking':
            return liquid + ":Sofi:Checking"
        case 'Sofi Savings':
            return liquid + ":Sofi:Savings"
        case 'Bing':
            return mr + ":" + accountName
        case 'Paidviewpoint':
            return mr + ":" + accountName  
        case 'Pinecone':
            return mr + ":" + accountName
        case 'Swagbucks':
            return mr + ":" + accountName
        case 'Tellwut':
            return mr + ":" + accountName
        case 'Brokerage':
            return nonLiquid + ":" + accountName
        case 'HSA Cash':
            return hsa + ":NM HSA Cash"
        case 'HSA Investment':
            return hsa + ":NM HSA Investment"
        case 'Vanguard401k':
            return v401k
        case 'VanguardPension':
            return nonLiquid + ":Pension"  
        case 'Total Stock Market(401k)':
            return v401k + ":Total Stock Market"
        case 'IRA':
            return ira + ":Fidelity"
        case 'Total Stock Market(IRA)':
            return ira + ":Fidelity:Total Stock Market" 
        case 'Total Intl Stock Market':
            return ira + ":Fidelity:Total Intl Stock Market"
        case 'Govt Money Market':
            return ira + ":Fidelity:Govt Money Market"
        case 'Ally':
            return assets + ":Ally Checking Account"
        case 'BoA-joint':
            return liabilities + ":BoA Credit Card"
        case 'Bonds':
            return bonds
        case 'MyConstant':
            return bonds + ":My Constant"
        case 'Worthy':
            return bonds + ":Worthy Bonds"
        case 'Home':
            return liabilities + ":Mortgage Loan"
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')
            
def scriptsToRun(date):
    match date.day:
        case 1:
            return ['Monthly USD', 'Monthly Crypto']
        case 5:
            return ['Barclays CC']
        case 6:
            return ['BoA CC']
        case 9:
            return ['Chase CC']        
        case 12:
            return ['Amex CC']
        case 13:
            scripts = ['Discover CC', 'Vanguard Pension', 'Update Personal Goals-Monthly']
            if date.month in [1,4,7,10]:
                scripts.append('Update Personal Goals-YTD')
            return scripts
        case 17:
            scripts = ['BoA-Joint CC', 'Update Joint Goals-Monthly']
            if date.month in [1,4,7,10]:
                scripts.append('Update Joint Goals-YTD')                
            return scripts
        case _:
            return []

def getScriptsToRun(context, today):
    context['scriptsToRunYesterday'] = scriptsToRun(today - timedelta(days=1))
    context['scriptsToRunToday'] = scriptsToRun(today)
    context['scriptsToRunTomorrow'] = scriptsToRun(today + timedelta(days=1))
    
def getPaycheckDates():
    paycheckDates = []
    firstPaycheckDate = datetime(2024,1,10,00,00).date()
    paycheckDates.append(firstPaycheckDate)
    previousPaycheck = firstPaycheckDate
    while True:
        nextPaycheck = previousPaycheck+relativedelta(weeks=2)
        if nextPaycheck.year != firstPaycheckDate.year:
            break
        else:
            paycheckDates.append(nextPaycheck)
        previousPaycheck = nextPaycheck
    return paycheckDates
    
def eventsHappening(date):
    events = []
    monthDates = getStartAndEndOfDateRange(date+relativedelta(months=+1), 'month')
    if date.day == monthDates['endDate'].day:
        events.append('Paycheck')
    if date in getPaycheckDates():
        events.append('Paycheck')
    match date.day:
        case 1:
            events.append('Pay Jon')
        case 3:
            events.append('Ally Interest')
        case 5:
            events.append('WE Energies')
        case 12:
            events.append('Mortgage Bill')
        case 13:
            events.append('BoA-Joint CC Bill posts')
        case 15:
            events.append('Paycheck')
        case 17:
            events.append('Schedule Ally transfer')
        case 24:
            events.append('Utility Bill posts')
        case _:
            return events
    return events

def getEventsHappening(context, today):
    context['eventsYesterday'] = eventsHappening(today - timedelta(days=1))
    context['eventsToday'] = eventsHappening(today)
    context['eventsTomorrow'] = eventsHappening(today + timedelta(days=1))

def returnRender(request, htmlPath, context):
    today = datetime.today().date()
    context['scriptCompleteTime'] = today
    getScriptsToRun(context, today)
    getEventsHappening(context, today)
    return render(request, htmlPath, context)
