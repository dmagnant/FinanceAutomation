import csv
import ctypes
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime, timedelta
from decimal import Decimal

import gspread
import piecash
import psutil
import pyautogui
import pygetwindow
import pyotp
from piecash import GnucashException, Price, Split, Transaction
from pycoingecko import CoinGeckoAPI
from pykeepass import PyKeePass
from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        InvalidArgumentException,
                                        NoSuchElementException,
                                        SessionNotCreatedException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def showMessage(header, body): 
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, body, header, 0)

def getOTP(account):
    return pyotp.TOTP(os.environ.get(account)).now()

def getUsername(directory, name):
    keepassFile = directory + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepassFile, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).username

def getPassword(directory, name):
    keepassFile = directory + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepassFile, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).password

def checkIfProcessRunning(processName):
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def startExpressVPN():
    os.startfile(r'C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe')
    time.sleep(4)
    EVPN = pygetwindow.getWindowsWithTitle('ExpressVPN')[0]
    time.sleep(1)
    EVPN.close()
    # stays open in system tray

def closeExpressVPN():
    if checkIfProcessRunning('ExpressVPN.exe'):
        os.startfile(r'C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe')
        time.sleep(3)
        EVPN = pygetwindow.getWindowsWithTitle('ExpressVPN')[0]
        EVPN.restore()
        EVPN.move(0, 0)
        EVPN.activate()
        pyautogui.leftClick(40, 50)
        time.sleep(1)
        pyautogui.leftClick(40, 280)

def openGnuCashBook(directory, type, readOnly, openIfLocked):
    if type == 'Finance':
        book = directory + r"\Finances\Personal Finances\Finance.gnucash"
    elif type == 'Home':
        book = directory + r"\Stuff\Home\Finances\Home.gnucash"
    try:
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    except GnucashException:
        showMessage("Gnucash file open", f'Close Gnucash file then click OK \n')
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    return myBook

def getAccountPath(account):
    match account:
        case 'ADA':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano"            
        case 'ALGO':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Algorand"
        case 'Ally':
            return "Assets:Ally Checking Account"
        case 'Amex':
            return "Liabilities:Credit Cards:Amex BlueCash Everyday"
        case 'ATOM':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cosmos"                  
        case 'Barclays':
            return "Liabilities:Credit Cards:BarclayCard CashForward"
        case 'BTC':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin"                
        case 'BTC-Midas':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin:BTC-Midas"
        case 'BTC-MyConstant':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin:BTC-MyConstant"                
        case 'BoA':
            return "Liabilities:Credit Cards:BankAmericard Cash Rewards"
        case 'BoA-joint':
            return "Liabilities:BoA Credit Card"
        case 'Chase':
            return "Liabilities:Credit Cards:Chase Freedom"
        case 'Crypto':
            return "Assets:Non-Liquid Assets:CryptoCurrency"
        case 'Discover':
            return "Liabilities:Credit Cards:Discover It"
        case 'DOT':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Polkadot"
        case 'ETH':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum"
        case 'ETH-Kraken':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Kraken"
        case 'ETH-Midas':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Midas"
        case 'ETH-MyConstant':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-MyConstant"
        case 'ETH2':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum2"
        case 'HSA':
            return "Liabilities:Credit Cards:Discover It"
        case 'IOTX':
            return "Assets:Non-Liquid Assets:CryptoCurrency:IoTex"
        case 'Liquid Assets':
            return "Assets:Liquid Assets"
        case 'M1':
            return "Assets:Liquid Assets:M1 Spend"               
        case 'MyConstant':
            return "Assets:Liquid Assets:My Constant"
        case 'PRE':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Presearch"
        case 'TIAA':
            return "Assets:Liquid Assets:TIAA"
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Worthy Bonds"
        case _:
            print(f'account: {account} not found in "getAccountPath" function')


def getGnuCashBalance(myBook, account):
    accountpath = getAccountPath(account)
    with myBook as book:
        balance = book.accounts(fullname=accountpath).get_balance()
    book.close()
    return balance

def setDirectory():
    return os.environ.get('StorageDirectory')

def configureDriverOptions(browser, asUser=True):
    if browser == "Edge":
        options = webdriver.EdgeOptions()
        if asUser:
            options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
    else:        
        options = webdriver.ChromeOptions()
    if browser == "Chrome":
        if asUser:
            options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Google\Chrome\User Data")
    elif browser == "Brave":
        options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        if asUser:
            options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\BraveSoftware\Brave-Browser\User Data")

    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("debuggerAddress","localhost:9222")
    # options.add_experimental_option("detach", True)
    options.add_argument("start-maximized")
    # profile = {"download.prompt_for_download": False}
    # options.add_experimental_option("prefs", profile)
    return options

def updateWebDriver(directory, browser, version):
    if (browser == "Chrome" or browser == "Brave"):
        url = "https://chromedriver.chromium.org/downloads"
        filePath = r"C:\Users\dmagn\Downloads\chromedriver_win32.zip"
        driver = openWebDriver(directory, "Edge", False)
        driver.implicitly_wait(5)
        driver.get(url)
        driver.find_element(By.PARTIAL_LINK_TEXT, "ChromeDriver " + version.partition('.')[0]).click()
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.find_element(By.PARTIAL_LINK_TEXT, "chromedriver_win32.zip").click()
    elif browser == "Edge":
        url = f"https://msedgedriver.azureedge.net/{version}/edgedriver_win64.zip"
        filePath = r"C:\Users\dmagn\Downloads\edgedriver_win64.zip"
        driver = openWebDriver(directory, "Chrome", False)
        driver.implicitly_wait(5)
        driver.get(url)
    time.sleep(3)
    with zipfile.ZipFile(filePath, 'r') as zip_ref:
        zip_ref.extractall(r"G:\My Drive\Projects\Coding\webdrivers")
    driver.quit()
    os.remove(filePath)
    if browser == "Edge":
        shutil.rmtree(r"G:\My Drive\Projects\Coding\webdrivers\Driver_Notes")

def openWebDriver(browser, asUser=True):
    directory = setDirectory()
    options = configureDriverOptions(browser, asUser)
    while(True):
        try:
            if browser == "Edge":
                versionBinaryPathText = " with binary path C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                return webdriver.Edge(service=Service(directory + r"\Projects\Coding\webdrivers\msedgedriver.exe"), options=options)
            elif browser == "Chrome":
                versionBinaryPathText = " with binary path C:\Program Files\Google\Chrome\Application\chrome.exe"
                return webdriver.Chrome(service=Service(directory + r"\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
            elif browser == "Brave":
                return webdriver.Chrome(service=Service(directory + r"\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
        except InvalidArgumentException:
            print('user profile already in use, opening blank window')
            options = configureDriverOptions(browser, False)
        except SessionNotCreatedException:
            error = str(sys.exc_info()[1]).partition('\n')[2].partition('\n')[0]
            version = error.replace("Current browser version is ", '').replace(versionBinaryPathText, '')
            updateWebDriver(directory, browser, version)

def updateSpreadsheet(directory, sheetTitle, tabTitle, account, month, value, symbol="$", modified=False):
    jsonCreds = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheet = sheet.worksheet(str(tabTitle))
    cell = getCell(account, month)
    if modified:
        cell = cell.replace(cell[0], chr(ord(cell[0]) + 3))
    sheetKey = getSheetKey(sheetTitle, tabTitle, worksheet, cell)
    if symbol == "$" or symbol == sheetKey:
        worksheet.update(cell, value)
    else:
        showMessage('Key Mismatch',     
        f'the given key: {symbol} does not match the sheet key: {sheetKey} for the cell that is being updated: {cell} \n'
        f'This is likely due to an update on the spreadsheet: {sheetTitle} > {tabTitle} \n'
        f'Check spreadsheet and verify the getCell method is getting the correct Cell')

def getCell(account, month):
    def getCellArray(account):
        match account:
            ## Asset Allocation Spreadsheet
            case 'Liquid Assets':
                return ['B6', 'I6', 'P6', 'B30', 'I30', 'P30', 'B54', 'I54', 'P54', 'B78', 'I78', 'P78']
            case 'Bonds':
                return ['F6', 'M6', 'T6', 'F30', 'M30', 'T30', 'F54', 'M54', 'T54', 'F78', 'M78', 'T78']
            case 'Vanguard401k':
                return ['B8', 'I8', 'P8', 'B32', 'I32', 'P32', 'B56', 'I56', 'P56', 'B80', 'I80', 'P80']
            case 'VanguardPension':
                return ['B10', 'I10', 'P10', 'B34', 'I34', 'P34', 'B58', 'I58', 'P58', 'B82', 'I82', 'P82']
            case 'Cryptocurrency':
                return ['B14', 'I14', 'P14', 'B36', 'I36', 'P36', 'B60', 'I60', 'P60', 'B84', 'I84', 'P84']
            case 'HE_HSA':
                return ['B12', 'I12', 'P12', 'B38', 'I38', 'P38', 'B62', 'I62', 'P62', 'B86', 'I86', 'P86']
            ## Checking Balance Spreadsheet(s)
            #Personal
            case 'BoA':
                return ['K5', 'S5', 'C40', 'K40', 'S40', 'C75', 'K75', 'S75', 'C110', 'K110', 'S110', 'C5']
            case 'Discover':
                return ['K6', 'S6', 'C41', 'K41', 'S41', 'C76', 'K76', 'S76', 'C111', 'K111', 'S111', 'C6']             
            case 'Amex':
                return ['K7', 'S7', 'C42', 'K42', 'S42', 'C77', 'K77', 'S77', 'C112', 'K112', 'S112', 'C7']
            case 'Chase':
                return ['F8', 'S8', 'C43', 'K43', 'S43', 'C78', 'K78', 'S78', 'C113', 'K113', 'S113', 'C8']            
            case 'Barclays':
                return ['K10', 'S10', 'C45', 'K45', 'S45', 'C80', 'K80', 'S80', 'C115', 'K115', 'S115', 'C10']
            #Joint
            case 'BoA-joint':
                return ['K16', 'S16', 'C52', 'K52', 'S52', 'C88', 'K88', 'S88', 'C124', 'K124', 'S124', 'C16']
            ## Cryptocurrency Spreadsheet
            case 'ALGO':
                return ['H2', 'J2']
            case 'BTC-Midas':
                return ['H3', 'J3']
            case 'BTC-MyConstant':
                return ['H4', 'J4']            
            case 'ADA':
                return ['H5', 'J5']            
            case 'ATOM':
                return ['H6', 'J6']
            case 'ETH-Midas':
                return ['H7', 'J7']
            case 'ETH-MyConstant':
                return ['H8', 'J8']            
            case 'ETH-Kraken':
                return ['H9', 'J9']
            case 'ETH2':
                return ['H10', 'J10']
            case 'IOTX':
                return ['H11', 'J11']
            case 'DOT':
                return ['H12', 'J12']            
            case 'PRE':
                return ['H13', 'J13']

    cell = (getCellArray(account))[month - 1]
    return cell

def getSheetKey(sheetTitle, tabTitle, worksheet, cellToUpdate):
    if sheetTitle == "Asset Allocation":
        if tabTitle == "Cryptocurrency":
            keyColumn = "B"
        else:
            keyColumn = "A"
    elif sheetTitle == "Checking Balance":
        keyColumn = "B"
    elif sheetTitle == "Home":
        if tabTitle == "Finances":
            keyColumn = "A"
        else:
            keyColumn = "B"
    worksheetKey = worksheet.acell(keyColumn + cellToUpdate[1:]).value
    return worksheetKey

def getStartAndEndOfPreviousMonth(today, month, year):
    if month == 1:
        startdate = today.replace(month=12, day=1, year=year - 1)
        enddate = today.replace(month=12, day=31, year=year - 1)
    elif month == 3:
        startdate = today.replace(month=2, day=1)
        enddate = today.replace(month=2, day=28)
    elif month in [5, 7, 10, 12]:
        startdate = today.replace(month=month - 1, day=1)
        enddate = today.replace(month=month - 1, day=30)
    else:
        startdate = today.replace(month=month - 1, day=1)
        enddate = today.replace(month=month - 1, day=31)
    return [startdate, enddate]

def getDateRange(today, numDays):
    # Gather last 3 days worth of transactions
    currentDate = today.date()    
    dateRange = currentDate.isoformat()
    day = 1
    while day <= numDays:
        dayBefore = (currentDate - timedelta(days=day)).isoformat()
        dateRange = dateRange + dayBefore
        day += 1
    return dateRange

def modifyTransactionDescription(description, amount="0.00"):
    if "INTERNET TRANSFER FROM ONLINE SAVINGS ACCOUNT XXXXXX9703" in description.upper():
        description = "Tessa Deposit"
    elif "PRIME TRUST LLC" in description.upper():
        description = "MyConstant transfer"
    elif "ALLY BANK $TRANSFER DAN" in description.upper():
        description = "Ally Transfer"
    elif "CITY OF MILWAUKE B2P*MILWWA" in description.upper():
        description = "Water Bill"
    elif "REQUESTED TRANSFER FROM DAN S MAGNANT" in description.upper():
        description = "Dan Deposit"
    elif "DOVENMUEHLE MTG MORTG PYMT" in description.upper():
        description = "Mortgage Payment"
    elif "TRANSFER TO M1 INVEST" in description.upper():
        description = "IRA Transfer"
    elif "INTEREST PAID TO M1 SPEND PLUS" in description.upper():
        description = "Interest paid"
    elif "NORTHWESTERN MUT" in description.upper():
        description = "NM Paycheck"
    elif "PAYPAL" in description.upper() and "10.00" in amount:
        description = "Swagbucks"  
    elif "PAYPAL" in description.upper():
        description = "Paypal"
    elif "LENDING CLUB" in description.upper():
        description = "Lending Club"
    elif "NIELSEN" in description.upper() and "3.00" in amount:
        description = "Pinecone Research"
    elif "VENMO" in description.upper():
        description = "Venmo"
    elif "TIAA" in description.upper():
        description = "TIAA Transfer"
    elif "TRANSFER FROM LINKED BANK" in description.upper():
        description = "TIAA Transfer"
    elif "ALLIANT CU XFER" in description.upper():
        description = "Alliant Transfer"        
    elif "AMEX EPAYMENT" in description.upper():
        description = "Amex CC"
    elif "COINBASE" in description.upper():
        description = "Crypto purchase"
    elif "CHASE CREDIT CRD RWRD" in description.upper():
        description = "Chase CC Rewards"
    elif "CHASE CREDIT CRD AUTOPAY" in description.upper():
        description = "Chase CC"
    elif "DISCOVER E-PAYMENT" in description.upper():
        description = "Discover CC"
    elif "DISCOVER CASH AWARD" in description.upper():
        description = "Discover CC Rewards"
    elif "BARCLAYCARD US CREDITCARD" in description.upper():
        description = "Barclays CC"
    elif "BARCLAYCARD US ACH REWARD" in description.upper():
        description = "Barclays CC Rewards"
    elif "BK OF AMER VISA ONLINE PMT" in description.upper():
        description = "BoA CC"
    elif "CASH REWARDS STATEMENT CREDIT" in description.upper():
        description = "BoA CC Rewards"
    return description

def setToAccount(account, row):
    toAccount = ''
    rowNum = 2 if account in ['BoA', 'BoA-joint', 'Chase', 'Discover'] else 1
    if "BoA CC" in row[rowNum]:
        if "Rewards" in row[rowNum]:
            toAccount = "Income:Credit Card Rewards"  
        else: 
            if account == 'Ally':
                toAccount = "Liabilities:BoA Credit Card"
            elif account == 'M1':
                toAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"
    elif "ARCADIA" in row[rowNum]:
        toAccount = ""
    elif "Tessa Deposit" in row[rowNum]:
        toAccount = "Tessa's Contributions"
    elif "MyConstant transfer" in row[rowNum]:
        toAccount = "Assets:Liquid Assets:My Constant"
    elif "Water Bill" in row[rowNum]:
        toAccount = "Expenses:Utilities:Water"
    elif "Dan Deposit" in row[rowNum]:
        toAccount = "Dan's Contributions"
    elif "Mortgage Payment" in row[rowNum]:
        toAccount = "Liabilities:Mortgage Loan"
    elif "Swagbucks" in row[rowNum]:
        toAccount = "Income:Market Research"
    elif "NM Paycheck" in row[rowNum]:
        toAccount = "Income:Salary"
    elif "GOOGLE FI" in row[rowNum].upper() or "GOOGLE *FI" in row[rowNum].upper():
        toAccount = "Expenses:Utilities:Phone"
    elif "TIAA Transfer" in row[rowNum]:
        toAccount = "Assets:Liquid Assets:TIAA"
    elif "Alliant Transfer" in row[rowNum]:
        toAccount = "Assets:Liquid Assets:Promos"        
    elif "CRYPTO PURCHASE" in row[rowNum].upper():
        toAccount = "Assets:Non-Liquid Assets:CryptoCurrency"
    elif "Pinecone Research" in row[rowNum]:
        toAccount = "Income:Market Research"
    elif "IRA Transfer" in row[rowNum]:
        toAccount = "Assets:Non-Liquid Assets:Roth IRA"
    elif "Lending Club" in row[rowNum]:
        toAccount = "Income:Investments:Interest"
    elif "CASH REWARDS STATEMENT CREDIT" in row[rowNum]:
        toAccount = "Income:Credit Card Rewards"        
    elif "Chase CC Rewards" in row[rowNum]:
        toAccount = "Income:Credit Card Rewards"
    elif "Chase CC" in row[rowNum]:
        toAccount = "Liabilities:Credit Cards:Chase Freedom"
    elif "Discover CC Rewards" in row[rowNum]:
        toAccount = "Income:Credit Card Rewards"        
    elif "Discover CC" in row[rowNum]:
        toAccount = "Liabilities:Credit Cards:Discover It"
    elif "Amex CC" in row[rowNum]:
        toAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
    elif "Barclays CC Rewards" in row[rowNum]:
        toAccount = "Income:Credit Card Rewards"
    elif "Barclays CC" in row[rowNum]:
        toAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
    elif "Ally Transfer" in row[rowNum]:
        toAccount = "Expenses:Joint Expenses"
    elif "BP#" in row[rowNum]:
        toAccount = "Expenses:Transportation:Gas (Vehicle)"
    elif "CAT DOCTOR" in row[rowNum]:
        toAccount = "Expenses:Medical:Vet"
    elif "PARKING" in row[rowNum] or "SPOTHERO" in row[rowNum].upper():
        toAccount = "Expenses:Transportation:Parking"
    elif "PROGRESSIVE" in row[rowNum]:
        toAccount = "Expenses:Transportation:Car Insurance"
    elif "SPECTRUM" in row[rowNum].upper():
            toAccount = "Expenses:Utilities:Internet"     
    elif "UBER" in row[rowNum].upper() and "EATS" in row[rowNum].upper():
        toAccount = "Expenses:Bars & Restaurants"
    elif "UBER" in row[rowNum].upper():
        toAccount = "Expenses:Travel:Ride Services" if account in ['BoA-joint', 'Ally'] else "Expenses:Transportation:Ride Services"
    elif "TECH WAY AUTO SERV" in row[rowNum].upper():
        toAccount = "Expenses:Transportation:Car Maintenance"
    elif "INTEREST PAID" in row[rowNum].upper():
        toAccount = "Income:Interest" if account in ['BoA-joint', 'Ally'] else "Income:Investments:Interest"
    if not toAccount:
        for i in ['HOMEDEPOT.COM', 'HOME DEPOT']:
            if i in row[rowNum].upper():
                if account in ['BoA-joint', 'Ally']:
                    toAccount = "Expenses:Home Depot"
    
    if not toAccount:
        for i in ['AMAZON', 'AMZN']:
            if i in row[rowNum].upper():
                toAccount = "Expenses:Amazon"

    if not toAccount:
        if len(row) >= 5:
            if row[3] == "Groceries" or row[4] == "Supermarkets":
                toAccount = "Expenses:Groceries"
        if not toAccount:
            for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET']:
                if i in row[rowNum].upper():
                    toAccount = "Expenses:Groceries"

    if not toAccount:
        if len(row) >= 5:
            if row[3] == "Food & Drink" or row[4] == "Restaurants":
                toAccount = "Expenses:Bars & Restaurants"
        if not toAccount:
            for i in ['MCDONALD', 'GRUBHUB', 'JIMMY JOHN', 'COLECTIVO', 'INSOMNIA', 'EATSTREET', "KOPP'S CUSTARD", 'MAHARAJA', 'STARBUCKS', "PIETRO'S PIZZA", 'SPROCKET CAFE']:
                if i in row[rowNum].upper():
                    toAccount = "Expenses:Bars & Restaurants"
    
    if not toAccount:
        toAccount = "Expenses:Other"
    return toAccount

def formatTransactionVariables(account, row):
    ccPayment = False
    description = row[1]
    if account == 'Ally':
        postDate = datetime.strptime(row[0], '%Y-%m-%d')
        description = row[1]
        amount = Decimal(row[2])
        fromAccount = "Assets:Ally Checking Account"
        reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
    elif account == 'Amex':
        postDate = datetime.strptime(row[0], '%m/%d/%Y')
        description = row[1]
        amount = -Decimal(row[2])
        if "AUTOPAY PAYMENT" in row[1]:
            ccPayment = True
        fromAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
        reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
    elif account == 'Barclays':
        postDate = datetime.strptime(row[0], '%m/%d/%Y')
        description = row[1]
        amount = Decimal(row[3])
        if "Payment Received" in row[1]:
            ccPayment = True
        fromAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
        reviewTransPath = row[0] + ", " + row[1] + ", " + row[3] + "\n"
    elif account == 'BoA':
        postDate = datetime.strptime(row[0], '%m/%d/%Y')
        description = row[2]
        amount = Decimal(row[4])
        if "BA ELECTRONIC PAYMENT" in row[2]:
            ccPayment = True
        fromAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"
        reviewTransPath = row[0] + ", " + row[2] + ", " + row[4] + "\n"
    elif account == 'BoA-joint':
        postDate = datetime.strptime(row[0], '%m/%d/%Y')
        description = row[2]
        amount = Decimal(row[4])
        if "BA ELECTRONIC PAYMENT" in row[2]:
            ccPayment = True
        fromAccount = "Liabilities:BoA Credit Card"
        reviewTransPath = row[0] + ", " + row[2] + ", " + row[4] + "\n"
    elif account == 'Chase':
        postDate = datetime.strptime(row[1], '%m/%d/%Y')
        description = row[2]
        amount = Decimal(row[5])
        if "AUTOMATIC PAYMENT" in row[2]:
            ccPayment = True
        fromAccount = "Liabilities:Credit Cards:Chase Freedom"
        reviewTransPath = row[1] + ", " + row[2] + ", " + row[5] + "\n"
    elif account == 'Discover':
        postDate = datetime.strptime(row[1], '%m/%d/%Y')
        description = row[2]
        amount = -Decimal(row[3])
        if "DIRECTPAY FULL BALANCE" in row[2]:
            ccPayment = True
        fromAccount = "Liabilities:Credit Cards:Discover It"
        reviewTransPath = row[1] + ", " + row[2] + ", " + row[3] + "\n"
    elif account == 'M1':
        postDate = datetime.strptime(row[0], '%Y-%m-%d')
        description = row[1]
        amount = Decimal(row[2])
        fromAccount = "Assets:Liquid Assets:M1 Spend"
        reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
    return [postDate, description, amount, ccPayment, fromAccount, reviewTransPath]

def importUniqueTransactionsToGnuCash(account, transactionsCSV, gnuCSV, myBook, driver, directory, dateRange, lineStart=1):
    importCSV = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\import.csv"
    open(importCSV, 'w', newline='').truncate()
    if account == 'Ally':
        gnuAccount = "Assets:Ally Checking Account"
    elif account == 'M1':
        gnuAccount = "Assets:Liquid Assets:M1 Spend"
    
    # retrieve transactions from GnuCash for the same date range
    transactions = [tr for tr in myBook.transactions
                    if str(tr.post_date.strftime('%Y-%m-%d')) in dateRange
                    for spl in tr.splits
                    if spl.account.fullname == gnuAccount]
    for tr in transactions:
        date = str(tr.post_date.strftime('%Y-%m-%d'))
        description = str(tr.description)
        for spl in tr.splits:
            amount = format(spl.value, ".2f")
            if spl.account.fullname == gnuAccount:
                row = date, description, str(amount)
                csv.writer(open(gnuCSV, 'a', newline='')).writerow(row)

    for row in csv.reader(open(transactionsCSV, 'r'), delimiter=','):
        if row not in csv.reader(open(gnuCSV, 'r'), delimiter=','):
            csv.writer(open(importCSV, 'a', newline='')).writerow(row)
    reviewTrans = importGnuTransaction(account, importCSV, myBook, driver, directory, lineStart)
    return reviewTrans

def importGnuTransaction(account, transactionsCSV, myBook, driver, directory, lineStart=1):
    reviewTrans = ''
    rowCount = 0
    lineCount = 0
    energyBillNum = 0
    for row in csv.reader(open(transactionsCSV), delimiter=','):
        rowCount += 1
        # skip header line
        if lineCount < lineStart:
            lineCount += 1
        else:
            transactionVariables = formatTransactionVariables(account, row)
            # Skip credit card payments from CC bills (already captured through Checking accounts)
            if transactionVariables[3]:
                continue
            else:
                description = modifyTransactionDescription(transactionVariables[1])
                postDate = transactionVariables[0]
                fromAccount = transactionVariables[4]
                amount = transactionVariables[2]
                toAccount = setToAccount(account, row)
                if 'ARCADIA' in description.upper():
                    energyBillNum += 1
                    amount = getEnergyBillAmounts(driver, directory, transactionVariables[2], energyBillNum)
                elif 'NM PAYCHECK' in description.upper() or "CRYPTO PURCHASE" in description.upper():
                    reviewTrans = reviewTrans + transactionVariables[5]
                else:
                    if toAccount == "Expenses:Other":
                        reviewTrans = reviewTrans + transactionVariables[5]
                writeGnuTransaction(myBook, description, postDate, amount, fromAccount, toAccount)
    return reviewTrans

def writeGnuTransaction(myBook, description, postDate, amount, fromAccount, toAccount=''):
    with myBook as book:
        if "Contribution + Interest" in description:
            split = [Split(value=amount[0], memo="scripted", account=myBook.accounts(fullname="Income:Investments:Interest")),
                    Split(value=amount[1], memo="scripted",account=myBook.accounts(fullname="Income:Employer Pension Contributions")),
                    Split(value=amount[2], memo="scripted",account=myBook.accounts(fullname=fromAccount))]
        elif "HSA Statement" in description:
            split = [Split(value=amount[0], account=myBook.accounts(fullname=toAccount)),
                    Split(value=amount[1], account=myBook.accounts(fullname=fromAccount[0])),
                    Split(value=amount[2], account=myBook.accounts(fullname=fromAccount[1]))]
        elif "ARCADIA" in description:
            split=[Split(value=amount[0], memo="Arcadia Membership Fee", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=amount[1], memo="Solar Rebate", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=amount[2], account=myBook.accounts(fullname="Expenses:Utilities:Electricity")),
                    Split(value=amount[3], account=myBook.accounts(fullname="Expenses:Utilities:Gas")),
                    Split(value=amount[4], account=myBook.accounts(fullname=fromAccount))]
        elif "NM Paycheck" in description:
            split = [Split(value=round(Decimal(2229.20), 2), memo="scripted",account=myBook.accounts(fullname=fromAccount)),
                    Split(value=round(Decimal(206.00), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:401k")),
                    Split(value=round(Decimal(5.49), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Dental")),
                    Split(value=round(Decimal(34.10), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Health")),
                    Split(value=round(Decimal(2.67), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Vision")),
                    Split(value=round(Decimal(202.39), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Social Security")),
                    Split(value=round(Decimal(47.33), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Medicare")),
                    Split(value=round(Decimal(415.83), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Federal Tax")),
                    Split(value=round(Decimal(159.07), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:State Tax")),
                    Split(value=round(Decimal(131.25), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:HSA")),
                    Split(value=-round(Decimal(3433.33), 2), memo="scripted",account=myBook.accounts(fullname=toAccount))]
        else:
            split = [Split(value=-amount, memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=amount, memo="scripted", account=myBook.accounts(fullname=fromAccount))]
        Transaction(post_date=postDate.date(), currency=myBook.currencies(mnemonic="USD"), description=description, splits=split)
        book.save()
        book.flush()
    book.close()

def getEnergyBillAmounts(driver, directory, amount, energyBillNum):
    if energyBillNum == 1:
        closeExpressVPN()
        # Get balances from Arcadia
        driver.execute_script("window.open('https://login.arcadia.com/email');")
        driver.implicitly_wait(5)
        # switch to last window
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        # get around bot-prevention by logging in twice
        num = 1
        while num <3:
            try:
                # click Sign in with email
                driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/div/div[1]/div/a").click()
                time.sleep(1)
            except NoSuchElementException:
                exception = "sign in page loaded already"
            try:
                # Login
                driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[1]/div[1]/input").send_keys(getUsername(directory, 'Arcadia Power'))
                time.sleep(1)
                driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[1]/div[2]/input").send_keys(getPassword(directory, 'Arcadia Power'))
                time.sleep(1)
                driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[2]/button").click()
                time.sleep(1)
                # Get Billing page
                driver.get("https://home.arcadia.com/dashboard/2072648/billing")
            except NoSuchElementException:
                exception = "already signed in"
            try: 
                driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/h1')
                num = 4
            except NoSuchElementException:
                num += 1
        if num == 3:
            showMessage("Login Check", 'Confirm Login to Arcadia, (manually if necessary) \n' 'Then click OK \n')
    else:
        # switch to last window
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.get("https://home.arcadia.com/dashboard/2072648/billing")
    statementRow = 1
    statementFound = "no"                     
    while statementFound == "no":
        # Capture statement balance
        arcadiaBalance = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/li[" + str(statementRow) + "]/div[2]/div/p")
        formattedAmount = "{:.2f}".format(abs(amount))
        if arcadiaBalance.text.strip('$') == formattedAmount:
            # click to view statement
            arcadiaBalance.click()
            statementFound = "yes"
        else:
            statementRow += 1
    # comb through lines of Arcadia Statement for Arcadia Membership (and Free trial rebate), Community Solar lines (3)
    arcadiaStatementLinesLeft = True
    statementRow = 1
    solar = 0
    arcadiaMembership = 0
    while arcadiaStatementLinesLeft:
        try:
            # read the header to get transaction description
            statementTrans = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/h2").text
            if statementTrans == "Arcadia Membership":
                arcadiaMembership = Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
                arcadiaamt = Decimal(arcadiaMembership)
            elif statementTrans == "Free Trial":
                arcadiaMembership = arcadiaMembership + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
            elif statementTrans == "Community Solar":
                solar = solar + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.replace('$',''))
            elif statementTrans == "WE Energies Utility":
                weBill = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text
            statementRow += 1
        except NoSuchElementException:
            arcadiaStatementLinesLeft = False
    arcadiaamt = Decimal(arcadiaMembership)
    solarAmount = Decimal(solar)
    # Get balances from WE Energies
    if energyBillNum == 1:
        driver.execute_script("window.open('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx');")
        # switch to last window
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        try:
            ## LOGIN
            driver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername(directory, 'WE-Energies (Home)'))
            driver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword(directory, 'WE-Energies (Home)'))
            # click Login
            driver.find_element(By.XPATH, "//*[@id='next']").click()
            time.sleep(4)
            # close out of app notice
            driver.find_element(By.XPATH, "//*[@id='notInterested']/a").click
        except NoSuchElementException:
            exception = "caught"
        # Click View bill history
        driver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click()
        time.sleep(4)
    billRow = 2
    billColumn = 7
    billFound = "no"
    # find bill based on comparing amount from Arcadia (weBill)
    while billFound == "no":
        # capture date
        weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
        weBillAmount = driver.find_element(By.XPATH, weBillPath).text
        if weBill == weBillAmount:
            billFound = "yes"
        else:
            billRow += 1
    # capture gas charges
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gasAmount = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    # capture electricity charges
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricityAmount = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    return [arcadiaamt, solarAmount, electricityAmount, gasAmount, amount]

def getCryptocurrencyPrice(coinList):
    coinGecko = CoinGeckoAPI()
    currency = 'usd'
    return coinGecko.get_price(ids=coinList, vs_currencies=currency)

def updateCryptoPriceInGnucash(symbol, coinPrice):
    directory = setDirectory()
    myBook = openGnuCashBook(directory, 'Finance', False, False)
    try: 
        gnuCashPrice = myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=datetime.today().date())  # raise a KeyError if Price does not exist
        gnuCashPrice.value = coinPrice
    except KeyError:
        p = Price(myBook.commodities(mnemonic=symbol), myBook.currencies(mnemonic="USD"), datetime.today().date(), coinPrice, "last")
    myBook.save()
    myBook.close()

def updateCryptoPrices():
    print('updating coin prices')
    directory = setDirectory()
    jsonCreds = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open('Asset Allocation')
    worksheet = sheet.worksheet(str('Cryptocurrency'))
    nameColumn = 'A'
    symbolColumn = 'B'
    priceColumn = 'J'
    row = 2
    stillCoins = True
    while stillCoins:
        coinName = worksheet.acell(nameColumn+str(row)).value
        if coinName != None:
            coinName = coinName.lower()
            coinSymbol = worksheet.acell(symbolColumn+str(row)).value
            if coinName == 'eth2':
                coinName = 'ethereum'
                coinSymbol = 'ETH'
            price = format(getCryptocurrencyPrice(coinName)[coinName]['usd'], ".2f")
            updateCryptoPriceInGnucash(coinSymbol, price)
            worksheet.update((priceColumn+str(row)), float(price))
            row += 1
        else:
            stillCoins = False

def updateCoinQuantityFromStakingInGnuCash(coinQuantity, coinSymbol):
    directory = setDirectory()
    myBook = openGnuCashBook(directory, 'Finance', False, False)
    gnuBalance = getGnuCashBalance(myBook, coinSymbol)
    coinDifference = Decimal(coinQuantity) - Decimal(gnuBalance)
    if coinDifference > 0:
        myBook = openGnuCashBook(directory, 'Finance', False, False)
        with myBook:
            split = [Split(value=-0, memo="scripted", account=myBook.accounts(fullname='Income:Investments:Staking')),
                    Split(value=0, quantity=round(Decimal(coinDifference), 6), memo="scripted", account=myBook.accounts(fullname=getAccountPath(coinSymbol)))]
            Transaction(post_date=datetime.today().date(), currency=myBook.currencies(mnemonic="USD"), description=coinSymbol + ' staking', splits=split)
            myBook.save()
            myBook.flush()
        myBook.close()
    elif coinDifference < 0:
        print(f'given balance of {coinQuantity} {coinSymbol} '
        f'minus gnuCash balance of {gnuBalance} '
        f'leaves unexpected coin difference of {coinDifference} '
        f'is it rounding issue?')

def getDollarsInvestedPerCoin(symbol):
    directory=setDirectory()
    # get dollars invested balance (must be run per coin)
    mybook = openGnuCashBook(directory, 'Finance', True, True)
    gnu_account = getAccountPath(symbol)
    total = 0
    # retrieve transactions from GnuCash
    transactions = [tr for tr in mybook.transactions
                    for spl in tr.splits
                    if spl.account.fullname == gnu_account]
    for tr in transactions:
        for spl in tr.splits:
            amount = format(spl.value, ".2f")
            if spl.account.fullname == gnu_account:
                total += abs(float(amount))
    print(f'total $ invested in {symbol}: ' + str(total))
    return total

def loginPiHole(directory, driver):
    driver.implicitly_wait(2)
    driver.get("http://192.168.1.144/admin/")
    driver.maximize_window()
    try:
        #click Login
        driver.find_element(By.XPATH, "/html/body/div[2]/aside/section/ul/li[3]/a").click()
        # Enter Password
        driver.find_element(By.ID, "loginpw").send_keys(getPassword(directory, 'Pi hole'))
        #click Login again
        driver.find_element(By.XPATH, "//*[@id='loginform']/div[2]/div/button").click()
        time.sleep(1)
    except NoSuchElementException:
        exception = "already logged in"

def disablePiHole(directory, driver):
    driver.maximize_window()
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(directory, driver)
    try:
        driver.find_element(By.XPATH, "//*[@id='pihole-disable']/a/span[2]").click()
        # Click Indefinitely
        driver.find_element(By.XPATH, "//*[@id='pihole-disable-indefinitely']").click()
    except ElementNotInteractableException:
        exception = "already disabled"

def enablePiHole(directory, driver):
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(directory, driver)
    try:
        driver.find_element(By.ID, "enableLabel").click()
    except NoSuchElementException:
        exception = "already enabled"
    except ElementNotInteractableException:
        exception = "already enabled"

def calculateNextRun(minsLeftForFaucet):
    now = datetime.now().time().replace(second=0, microsecond=0)
    if now.hour == 23:
        nextRunMinute = 0
        nextRunHour = 0
    elif now.hour == 18:
        nextRunMinute = 0
        nextRunHour = 19
        minsLeftForFaucet = 61 - now.minute
    else:
        nextRunMinute = now.minute + minsLeftForFaucet
        nextRunHour = now.hour
        if (nextRunMinute >= 60):
            nextRunMinute = abs(nextRunMinute - 60)
            nextRunHour += 1 if nextRunHour < 23 else 0
    if nextRunMinute < 0 or nextRunMinute > 59:
        showMessage('Next Run Minute is off', 'Nextrunminute = ' + str(nextRunMinute))
    nextRun = now.replace(hour=nextRunHour, minute=nextRunMinute)
    print('next run at ', str(nextRun.hour) + ":" + "{:02d}".format(nextRun.minute))
    if nextRun.hour == 0:
        minsLeftForFaucet -= datetime.now().time().minute
    time.sleep(minsLeftForFaucet * 60)
