import time, csv, json, os
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys


if __name__ == '__main__' or __name__ == "Webull":
    from Classes.Asset import USD, Security
    from Classes.GnuCash import GnuCash, createNewTestBook
    from Classes.WebDriver import Driver
    from Classes.Spreadsheet import Spreadsheet
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP)    
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash, createNewTestBook
    from .Classes.Spreadsheet import Spreadsheet
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP)    

def unlockTrading(driver):
    try:
        driver.webDriver.find_element(By.PARTIAL_LINK_TEXT,'unlock').click()
        driver.webDriver.find_element(By.XPATH,'/html/body/div[5]/div[1]/div/div[2]/div[2]/div/input').send_keys(str(json.loads(getNotes('Webull'))['TradingPassword']))           
    except NoSuchElementException:  
        exception = 'trading unlocked'

def getWebullAccounts(book):
    accounts = {}
    accounts['WebullBrokerage'] = USD('WebullBrokerage', book)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        for child in account.gnuCashAccount.children:
            if child.name == 'Options' or child.name == 'Cash':
                accounts[accountName + child.name] = USD(account.name + child.name, book)
    return accounts

def getWebullCSVFile(account):
    accountSuffix = f"{account}"
    return setDirectory() + rf"\Projects\Coding\Python\FinanceAutomation\Resources\{accountSuffix}.csv"

def locateWebullWindow(driver):
    found = driver.findWindowByUrl("app.webull.com/account")
    if not found:   webullLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def webullLogin(driver):
    driver.openNewWindow('https://www.webull.com')
    login = driver.clickXPATHElementOnceAvailable('/html/body/div/section/header/div/div[2]/div/button[2]') # login
    if login:
        time.sleep(1)
        # driver.webDriver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/div/div/span/input').send_keys(os.environ.get('Phone')) # enter phone as user
        driver.webDriver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div[5]/div[3]/div/span/input').send_keys(getPassword('Webull')) # enter password
        driver.webDriver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[5]/div[4]/button/span').click() # Log In
        if driver.getXPATHElementOnceAvailable('/html/body/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/input'): # 2FA Code
            showMessage('Enter 2FA Code', 'Enter Code Manually, then click OK here')
            driver.webDriver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/button').click() # Next
    driver.webDriver.get('https://app.webull.com/account')
    unlockTrading(driver)


def getWebullCashBalanceElement(column): return f"/html/body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[3]/div[3]/div/div/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[{str(column)}]/span"

def getWebullBalance(driver, accounts):
    locateWebullWindow(driver)
    unlockTrading(driver)
    accounts['WebullBrokerage'].balance = float(driver.getXPATHElementTextOnceAvailable("/html/body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[2]/div[1]/div[2]/span").replace(',',''))
    column = 1
    description = driver.getXPATHElementTextOnceAvailable(getWebullCashBalanceElement(column))
    if description == 'Cash Balance':
        column +=1
        accounts['WebullBrokerageCash'].balance = float(driver.getXPATHElementTextOnceAvailable(getWebullCashBalanceElement(column)).replace(',',''))
    accounts['WebullBrokerageOptions'].balance = round(accounts['WebullBrokerage'].balance - accounts['WebullBrokerageCash'].balance,2)

def getWebullOptionsValueAndCost(driver, allAccounts, book, accountToGet='all'):
    locateWebullWindow(driver)
    unlockTrading(driver)
    shortPutTotal = 0
    marketValueTotal = 0
    costTotal = 0
    row = 2
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_0']/span") # Positions
    driver.clickXPATHElementOnceAvailable("//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[1]") # My Positions
    while True:
        marketValueAmount = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[5]")
        if marketValueAmount != False:
            marketValueTotal += float(marketValueAmount)
            costTotal += float(driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[8]"))
            if float(marketValueAmount) < 0:    shortPutTotal += float(marketValueAmount)
            row+=1
        else:
            break
    allAccounts['WebullBrokerageOptions'].balance = marketValueTotal
    allAccounts['WebullBrokerageOptions'].cost = costTotal

def webullTransactionMatchesBasedOnDetails(driver, ohDateTime, dateTime, description, ohRow, amount):
    if ohDateTime.date() == dateTime.date():
        side = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]") # Side (buy/sell)
        ohSymbol = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[2]")[:4].replace(' ', '') # Symbol
        if 'Bought' in description and side == 'Buy':
            description = description.replace('Bought ', '')
            symbol = description[:4].replace(' ', '')
        elif 'Sold' in description and side == 'Sell':
            description = description.replace('Sold ', '')
            symbol = description[:4].replace(' ', '')
        else:
            return False
        if ohSymbol == symbol:
            quantity = float(driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[8]")) # Filled Qty
            price = float(driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[10]")) # Average Price
            ohAmount = quantity * price
            if 'Buy' in description:    ohAmount *= -1
            if 'Call' in description or 'Put' in description:   ohAmount *=100
            if abs(ohAmount) - abs(amount) <= 0.50:
                return True
    return False

def getWebullOderHistoryDetails(driver, dateTime, description, adRow, amount):
    actionChains = ActionChains(driver.webDriver)
    firstCompletePassDone = False
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_0']/span") # Positions
    driver.clickXPATHElementOnceAvailable("//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[3]") # Order History    
    ohRow = adRow-1
    fee = 0
    while True:
        ohRow+=1
        ohRawDateTime = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[9]") # filled time
        if ohRawDateTime == False:  break
        elif ohRawDateTime != '':   ohDateTime = datetime.strptime(ohRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
        else:                       continue
        if ohDateTime == dateTime or (firstCompletePassDone and webullTransactionMatchesBasedOnDetails(driver, ohDateTime, dateTime, description, ohRow, amount)):
            ohDescription = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[2]") # Symbol
            if 'Put' in ohDescription or 'Call' in ohDescription:
                description = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]") + ' ' + ohDescription # Side (buy/sell)
            actionChains.context_click(driver.webDriver.find_element(By.XPATH,f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[2]")).perform() # right-click on row
            driver.clickXPATHElementOnceAvailable("/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[1]") # Order Details
            odRow = 1
            while True:
                odRow+=1
                feeDescription = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[1]", wait=1)
                if feeDescription:
                    if feeDescription == 'Transaction Fee':
                        feeText = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[2]", wait=1).replace('$', '')
                        if feeText != '--':
                            fee = float(feeText)
                        break
                    elif feeDescription == 'Order Status':
                        odRow+=1 # skip extra row which is divider between order status and transaction fee
                else:   break
            driver.webDriver.refresh()
            break
        elif ohDateTime < dateTime: 
            if not firstCompletePassDone:
                firstCompletePassDone = True
                ohRow = adRow-1
            else:
                break # no more transactions for this date
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_1']/span") # Account Details
    return {'fee': fee, 'description': description}

def captureWebullTransactions(driver, dateRange): # CAN IMPROVE THIS BY PULLING DATE, DESCRIPTION, AMOUNT FROM ACCOUNT DETAILS, THEN FEE FROM POSITIONS>ORDER HISTORY
    locateWebullWindow(driver)
    WebullActivity = getWebullCSVFile("WebullOptions")
    open(WebullActivity, 'w', newline='').truncate()
    adRow = 1
    # check Account Details Page for true cash amount of transaction
    if driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_1']/span"): # Account Details
        while True:
            adRow+=1
            adRawDateTime = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[3]") # Date
            if adRawDateTime:
                adDateTime = datetime.strptime(adRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
                if adDateTime.date() >= dateRange['startDate'] and adDateTime.date() <= dateRange['endDate']:
                    amount = float(driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[4]").replace('+','').replace(',','')) # Amount
                    description = driver.getXPATHElementTextOnceAvailable(f"//*[@id='app']/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[2]") # Description
                    details = getWebullOderHistoryDetails(driver, adDateTime, description, adRow, amount)
                    transaction = adDateTime.date(), details['description'], round(amount,2), details['fee']
                    csv.writer(open(WebullActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                else:   break # no more transactions in date range
            else:       break # no more transactions or error finding date
    else:               showMessage('Error', 'Account Details not found')
    return WebullActivity

def writeWebullOptionMarketChangeTransaction(accounts, book):
    splits, createdSplits=[], []
    account = accounts['WebullBrokerageOptions']
    marketChange = 0
    if account.balance:
        gnuBalance = book.getGnuAccountBalance(account.gnuAccount)
        account.updateGnuBalance(gnuBalance)
        change = Decimal(account.balance) - account.gnuBalance
        if change:
            splits.append({'amount': round(change, 2), 'account': account.gnuAccount})
            marketChange += change
    if marketChange:
        splits.append({'amount': -round(marketChange,2), 'account': "Income:Investments:Market Change"})
        for spl in splits:  createdSplits.append(book.createSplit(spl['amount'], spl['account']))
        book.writeTransaction(datetime.today().date(), "Options Market Change", createdSplits)
        if not account.balance:
            account.balance = Decimal(0.00)
        account.updateGnuBalance(account.balance)

def importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(accounts['WebullBrokerageOptions'].gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(WebullActivity), delimiter=','):
        description = row[1]
        if 'transfer' in description.lower(): continue
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        amount = Decimal(row[2])
        fee = round(Decimal(row[3]),2)
        fromAccount = accounts['WebullBrokerageOptions'].gnuAccount
        toAccount = accounts['WebullBrokerageCash'].gnuAccount
        splits = []
        if fee:
            splits.append({'amount': fee, 'account': book.getGnuAccountFullName('Bank Fees')})
        splits.append({'amount': amount, 'account': toAccount})
        splits.append({'amount': -(amount), 'account': fromAccount})
        if 'Buy' in description or 'Sell' in description: # Options Transaction
            premium = abs(amount) + fee
            premium *= -1
            if amount < 0: 
                # premium *= -1 # opposite options sign
                amount *= -1
            splits.append({'amount': premium, 'account': book.getGnuAccountFullName('Premiums')})
            splits.append({'amount':amount, 'account':book.getGnuAccountFullName('Market Change')})
        book.writeUniqueTransaction(accounts['WebullBrokerageOptions'], existingTransactions, postDate, description, splits)

def runWebullDaily(driver, accounts, book, gnuCashTransactions, dateRange):
    locateWebullWindow(driver)
    getWebullBalance(driver, accounts)
    WebullActivity = captureWebullTransactions(driver, dateRange)
    importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions)
    getWebullOptionsValueAndCost(driver, accounts, book)
    writeWebullOptionMarketChangeTransaction(accounts, book)
    for accountName in list(accounts.keys()): # update balances for ALL
        account = accounts.get(accountName)
        balance = book.getGnuAccountBalance(account.gnuAccount)
        if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
        else:                           account.updateGnuBalance(balance)

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     dateRange = getStartAndEndOfDateRange(timeSpan=20)
#     gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
#     accounts = getWebullAccounts(book)
#     locateWebullWindow(driver)
#     WebullActivity = getWebullCSVFile("WebullOptions")
#     # WebullActivity = captureWebullTransactions(driver, dateRange)
#     importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions)
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateWebullWindow(driver)
    unlockTrading(driver)