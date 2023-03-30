import ctypes
import os
import time
from datetime import timedelta
from decimal import Decimal

import psutil
import pyotp
from pycoingecko import CoinGeckoAPI
from pykeepass import PyKeePass
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

def showMessage(header, body): 
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, body, header, 0)
    
def setDirectory():
    return os.environ.get('StorageDirectory')    

def isProcessRunning(processName):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
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
        #click Login
        driver.find_element(By.XPATH, "/html/body/div[2]/aside/section/ul/li[3]/a").click()
        # Enter Password
        driver.find_element(By.ID, "loginpw").send_keys(getPassword('Pi hole'))
        #click Login again
        driver.find_element(By.XPATH, "//*[@id='loginform']/div[2]/div/button").click()
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
        # Click Indefinitely
        driver.find_element(By.XPATH, "//*[@id='pihole-disable-indefinitely']").click()
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
    driver.webDriver.close()
    driver.switchToLastWindow()
    driver.webDriver.implicitly_wait(3)
    return round(Decimal(price), 2)

def modifyTransactionDescription(description, amount="0.00"):
    if "INTERNET TRANSFER FROM ONLINE SAVINGS ACCOUNT XXXXXX9703" in description.upper():
        description = "Tessa Deposit"
    elif "INTEREST EARNED" in description.upper():
        description = "Interest earned"
    elif "SOFI REWARDS REDEMPTION" in description.upper():
        description = "Interest earned"
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
    elif "DOVENMUEHLE MTG MORTG PYMT" in description.upper():
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
    elif "SPECTRUM" in description.upper():
        description = "Internet Bill"
    elif "COINBASE" in description.upper():
        description = "Crypto purchase"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) > 0:
        description = "Chase CC Rewards"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) < 0:
        description = "Chase CC"
    elif "DISCOVER CASH AWARD" in description.upper():
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
            return "Assets:Liquid Assets:Bonds"
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
        case 'Fidelity':
            return "Assets:Non-Liquid Assets:IRA:Fidelity"
        case 'HSA':
            return "Assets:Non-Liquid Assets:HSA:NM HSA"
        case 'Home':
            return "Liabilities:Mortgage Loan"
        case 'IoTex':
            return "Assets:Non-Liquid Assets:CryptoCurrency:IoTex"
        case 'Liquid Assets':
            return "Assets:Liquid Assets"
        case 'Loopring':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Loopring"              
        case 'MyConstant':
            return "Assets:Liquid Assets:Bonds:My Constant"
        case 'Presearch':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Presearch"
        case 'Sofi Checking':
            return "Assets:Liquid Assets:Sofi:Checking"
        case 'Sofi Savings':
            return "Assets:Liquid Assets:Sofi:Savings"
        case 'Vanguard401k':
            return "Assets:Non-Liquid Assets:401k"                         
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Bonds:Worthy Bonds"
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
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')
