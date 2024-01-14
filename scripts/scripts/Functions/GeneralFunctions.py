import ctypes
import os
import time
from datetime import timedelta
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
            endDate = today.replace(month=2, day=28)
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
        description = "Fidelity IRA Transfer"
    elif "CITY OF MILWAUKE B2P*MILWWA" in description.upper():
        description = "Water Bill"
    elif "COOPER NSM" in description.upper():
        description = "Mortgage Payment"
    elif "NORTHWESTERN MUT" in description.upper():
        description = "NM Paycheck"
    elif "PAYPAL" in description.upper() and "10.00" in amount:
        description = "Swagbucks"  
    elif "PAYPAL" in description.upper():
        description = "Paypal"
    elif "NIELSEN" in description.upper() and "3.00" in amount:
        description = "Pinecone Research"
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
    match accountName:
        case 'Cardano':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano"
        case 'ADA-Eternl':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano:ADA-Eternl"    
        case 'ADA-Nami':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano:ADA-Nami"    
        case 'Algorand':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Algorand"
        case 'Ally':
            return "Assets:Ally Checking Account"
        case 'AmazonGC':
            return "Assets:Liquid Assets:Amazon GC"
        case 'Amex':
            return "Liabilities:Credit Cards:Amex BlueCash Everyday"
        case 'Cosmos':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cosmos"                  
        case 'Barclays':
            return "Liabilities:Credit Cards:BarclayCard CashForward"
        case 'Bitcoin':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin"                               
        case 'BoA':
            return "Liabilities:Credit Cards:BankAmericard Cash Rewards"
        case 'BoA-joint':
            return "Liabilities:BoA Credit Card"
        case 'Bonds':
            return "Liabilities:Bonds"
        case 'Chase':
            return "Liabilities:Credit Cards:Chase Freedom"
        case 'Crypto':
            return "Assets:Non-Liquid Assets:CryptoCurrency"
        case 'Discover':
            return "Liabilities:Credit Cards:Discover It"
        case 'Polkadot':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Polkadot"
        case 'Ethereum':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum"
        case 'ETH-Kraken':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Kraken"
        case 'ETH-Ledger':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Ledger"
        case 'Ethereum2':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum2"
        case 'IRA':
            return "Assets:Non-Liquid Assets:IRA:Fidelity"
        case 'Brokerage':
            return "Assets:Non-Liquid Assets:Brokerage"
        case 'HSA Cash':
            return "Assets:Non-Liquid Assets:HSA:NM HSA Cash"
        case 'HSA Investment':
            return "Assets:Non-Liquid Assets:HSA:NM HSA Investment"           
        case 'Home':
            return "Liabilities:Mortgage Loan"
        case 'IoTex':
            return "Assets:Non-Liquid Assets:CryptoCurrency:IoTex"
        case 'Liquid Assets':
            return "Assets:Liquid Assets"
        case 'Loopring':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Loopring"              
        case 'MyConstant':
            return "Liabilities:Bonds:My Constant"
        case 'Presearch':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Presearch"
        case 'Ripple':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ripple"
        case 'Sofi Checking':
            return "Assets:Liquid Assets:Sofi:Checking"
        case 'Sofi Savings':
            return "Assets:Liquid Assets:Sofi:Savings"
        case 'Vanguard401k':
            return "Assets:Non-Liquid Assets:401k"                         
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Liabilities:Bonds:Worthy Bonds"
        case 'Bing':
            return "Assets:Liquid Assets:MR:Bing"
        case 'Paidviewpoint':
            return "Assets:Liquid Assets:MR:Paidviewpoint"        
        case 'Pinecone':
            return "Assets:Liquid Assets:MR:Pinecone"
        case 'Swagbucks':
            return "Assets:Liquid Assets:MR:Swagbucks"
        case 'Tellwut':
            return "Assets:Liquid Assets:MR:Tellwut"
        case 'Real Estate Index Fund':
            return "Assets:Non-Liquid Assets:401k:Real Estate Index Fund"
        case 'Total Stock Market(401k)':
            return "Assets:Non-Liquid Assets:401k:Total Stock Market"
        case 'Total Stock Market(IRA)':
            return "Assets:Non-Liquid Assets:IRA:Fidelity:Total Stock Market" 
        case 'Total Intl Stock Market':
            return "Assets:Non-Liquid Assets:IRA:Fidelity:Total Intl Stock Market"
        case 'Govt Money Market':
            return "Assets:Non-Liquid Assets:IRA:Fidelity:Govt Money Market"
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')

def returnRender(request, htmlPath, context):
    context['scriptCompleteTime'] = datetime.today()
    return render(request, htmlPath, context)
