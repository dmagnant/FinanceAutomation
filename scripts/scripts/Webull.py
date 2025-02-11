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
        time.sleep(1)
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

def getWebullBrokerageTotalBalance(driver, path):
    balance = driver.getXPATHElementTextOnceAvailable(path)
    if balance:
        balance = float(balance.replace(',',''))
    return balance

def getWebullBalanceByPath(driver, path):
    balance = driver.getXPATHElementTextOnceAvailable(path)
    if balance:
        balance = float(balance.replace(',',''))
    return balance

def getWebullBalance(driver, accounts):
    locateWebullWindow(driver)
    unlockTrading(driver)
    accounts['WebullBrokerage'].balance = getWebullBalanceByPath(driver, "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[1]/div/div[2]/div[1]/div[2]/span")
    if not accounts['WebullBrokerage'].balance:
        showMessage('Failed to find balance', 'No balance found for ' + accounts['WebullBrokerage'].name)
    accounts['WebullBrokerageCash'].balance = getWebullBalanceByPath(driver, "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[1]/div/div[2]/div[2]/li/span[2]/span")
    if not accounts['WebullBrokerageCash'].balance:
        showMessage('Failed to find balance', 'No balance found for ' + accounts['WebullBrokerageCash'].name)    
    accounts['WebullBrokerageOptions'].balance = round(accounts['WebullBrokerage'].balance - accounts['WebullBrokerageCash'].balance,2)

def getWebullOptionsCost(driver, allAccounts, accountToGet='all'):
    locateWebullWindow(driver)
    unlockTrading(driver)
    costTotal = 0
    row = 2
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_0']/span") # Positions
    driver.clickXPATHElementOnceAvailable("/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[1]") # My Positions
    while True:
        costAmount = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[8]")
        if costAmount != False:
            costTotal += float(costAmount)
            row+=1
        else:
            break
    allAccounts['WebullBrokerageOptions'].cost = costTotal

def webullTransactionMatchesBasedOnDetails(driver, ohDateTime, dateTime, description, ohRow, amount):
    if ohDateTime.date() == dateTime.date():
        side = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]") # Side (buy/sell)
        ohSymbol = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[2]")[:4].replace(' ', '') # Symbol
        if 'Bought' in description and side == 'Buy':
            description = description.replace('Bought ', '')
            symbol = description[:4].replace(' ', '')
        elif 'Sold' in description and side == 'Sell':
            description = description.replace('Sold ', '')
            symbol = description[:4].replace(' ', '')
        else:
            return False
        if ohSymbol == symbol:
            quantity = float(driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[8]")) # Filled Qty
            price = float(driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[10]")) # Average Price
            ohAmount = quantity * price
            if 'Buy' in description:    ohAmount *= -1
            if 'Call' in description or 'Put' in description:   ohAmount *=100
            if abs(ohAmount) - abs(amount) <= 0.50:
                return True
    return False

def getWebullOrderHistoryDetails(driver, dateTime, description, amount, startRow):
    actionChains = ActionChains(driver.webDriver)
    firstCompletePassDone = False
    returnRow = startRow
    ohRow = startRow-1
    fee = 0
    dateTime = datetime.strptime(dateTime, '%Y-%m-%d %H:%M:%S')
    amount = float(amount)
    while True:
        ohRow+=1
        ohRawDateTime = driver.getElementTextAndLocate(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[9]", By.XPATH, wait=2) # filled time
        if ohRawDateTime == False:
            break
        elif ohRawDateTime != '':   ohDateTime = datetime.strptime(ohRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
        else:                       continue
        if ohDateTime == dateTime or (firstCompletePassDone and webullTransactionMatchesBasedOnDetails(driver, ohDateTime, dateTime, description, ohRow, amount)):
            returnRow = ohRow
            ohDescription = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[2]", wait=2) # Symbol
            if 'Put' in ohDescription or 'Call' in ohDescription:
                description = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]", wait=2) + ' ' + ohDescription # Side (buy/sell)
            actionChains.context_click(driver.webDriver.find_element(By.XPATH,f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]")).perform() # right-click on row
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
            driver.getXPATHElementOnceAvailable('/html/body').send_keys(Keys.ESCAPE) # close pop-up window
            break
        elif ohDateTime.date() < dateTime.date(): 
            if not firstCompletePassDone:
                print('first complete pass done')
                firstCompletePassDone = True
                ohRow = startRow-1
            else:
                break # no more transactions for this date
        else:
            continue
    return {'fee': fee, 'description': description, 'ohRow': returnRow}

def captureWebullTransactions(driver, dateRange): # CAN IMPROVE THIS BY PULLING DATE, DESCRIPTION, AMOUNT FROM ACCOUNT DETAILS, THEN FEE FROM POSITIONS>ORDER HISTORY
    locateWebullWindow(driver)
    WebullActivity = getWebullCSVFile("WebullOptions")
    open(WebullActivity, 'w', newline='').truncate()
    # check Account Details Page for true cash amount of transaction
    accountDetails = driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_1']/span") # Account Details
    if accountDetails == False:
        showMessage('Error', 'Account Details button not found')
        return
    driver.clickXPATHElementOnceAvailable('/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/span/div/span', wait=2) # Date Range
    driver.clickXPATHElementOnceAvailable('/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[3]/span', wait=2) # 3M
    adRow = 1
    while True:
        adRow+=1
        adRawDateTime = driver.getElementTextAndLocate(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[3]/span", By.XPATH) # Date
        if adRawDateTime:
            adDateTime = datetime.strptime(adRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
            if adDateTime.date() >= dateRange['startDate'] and adDateTime.date() <= dateRange['endDate']:
                amount = float(driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[4]").replace('+','').replace(',','')) # Amount
                description = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[2]") # Description
                csv.writer(open(WebullActivity, 'a', newline='', encoding="utf-8")).writerow([adDateTime, description, round(amount,2)])
            else:   break # no more transactions in date range
        else:       break # no more transactions or error finding date

    # check Positions > Order History for fees and description
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_0']/span") # Positions
    history = driver.clickXPATHElementOnceAvailable("/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[3]") # Order History
    
    if history == False:
        showMessage('Error', 'Order History button not found')
    ohRow = 2
    rows = list(csv.reader(open(WebullActivity), delimiter=','))
    for row in rows:
        print(f'getting details for row: {row}')
        # details = getWebullOrderHistoryDetails(driver, row[0], row[1], row[2], 2) # hardcode at first row for now
        details = getWebullOrderHistoryDetails(driver, row[0], row[1], row[2], ohRow)
        print(f'details for row: {details}')
        row[0] = row[0][:-9] # remove timezone
        row[1] = details['description']
        row.append(details['fee'])
        ohRow = 2 if details['ohRow'] - 15 < 2 else details['ohRow'] - 15

    csv.writer(open(WebullActivity, 'w', newline='')).writerows(rows)
    return WebullActivity

def captureWebullTransactionsModified(driver, dateRange): # CAN IMPROVE THIS BY PULLING DATE, DESCRIPTION, AMOUNT FROM ACCOUNT DETAILS, THEN FEE FROM POSITIONS>ORDER HISTORY
    locateWebullWindow(driver)
    WebullActivity = getWebullCSVFile("WebullOptions")
    open(WebullActivity, 'w', newline='').truncate()
    actionChains = ActionChains(driver.webDriver)
    # check Account Details Page for true cash amount of transaction
    accountDetails = driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_1']/span") # Account Details
    if accountDetails == False:
        showMessage('Error', 'Account Details button not found')
        return
    driver.clickXPATHElementOnceAvailable('/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/span/div/span', wait=2) # Date Range
    driver.clickXPATHElementOnceAvailable('/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[3]/span', wait=2) # 3M
    adRow = 1
    transactions = {}
    while True:
        adRow+=1
        adRawDateTime = driver.getElementTextAndLocate(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[3]/span", By.XPATH) # Date
        if adRawDateTime:
            adDateTime = datetime.strptime(adRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
            if adDateTime.date() >= dateRange['startDate'] and adDateTime.date() <= dateRange['endDate']:
                description = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[2]") # Description
                if 'transfer' in description.lower(): 
                    continue
                amount = float(driver.getXPATHElementTextOnceAvailable(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[4]").replace('+','').replace(',','')) # Amount
                if amount <0:
                    options = premium = -(abs(amount)-fee)
                else:
                    options = -(amount)
                    premium = -(amount-fee)
                interest = amount if 'interest' in description.lower() else 0
                if adDateTime.date() not in transactions:
                    transactions[adDateTime.date()] = {'amount': amount, 'fee': 0, 'interest': interest}
                else:
                    transactions[adDateTime.date()]['amount'] += amount
                    transactions[adDateTime.date()]['interest'] += interest
                # csv.writer(open(WebullActivity, 'a', newline='', encoding="utf-8")).writerow([adDateTime, description, round(amount,2)])
            else:   break # no more transactions in date range
        else:       break # no more transactions or error finding date

    # check Positions > Order History for fees
    driver.clickXPATHElementOnceAvailable("//*[@id='tabs_lv2_0']/span") # Positions
    history = driver.clickXPATHElementOnceAvailable("/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[3]") # Order History
    if history == False:
        showMessage('Error', 'Order History button not found')
    ohRow = 1
    while True:
        ohRow+=1
        ohRawDateTime = driver.getElementTextAndLocate(f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[9]", By.XPATH, wait=2) # filled time
        if ohRawDateTime == False:  break # failed to find date
        elif ohRawDateTime != '':   
            ohDateTime = datetime.strptime(ohRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
            if ohDateTime.date() in transactions:
                actionChains.context_click(driver.webDriver.find_element(By.XPATH,f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(ohRow)}]/td[3]")).perform() # right-click on row
                driver.clickXPATHElementOnceAvailable("/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[1]") # Order Details
                odRow = 1
                while True:
                    odRow+=1
                    feeDescription = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[1]", wait=1)
                    if feeDescription:
                        if feeDescription == 'Transaction Fee':
                            feeText = driver.getXPATHElementTextOnceAvailable(f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[2]", wait=1).replace('$', '')
                            if feeText != '--':
                                transactions[ohDateTime.date()]['fee'] += float(feeText)
                            break
                        elif feeDescription == 'Order Status':
                            odRow+=1 # skip extra row which is divider between order status and transaction fee
                    else:   break
                driver.getXPATHElementOnceAvailable('/html/body').send_keys(Keys.ESCAPE) # close pop-up window
            else:
                break # outside date range
        else:                    
            continue # skip canceled order
    for date in transactions:
        csv.writer(open(WebullActivity, 'a', newline='', encoding="utf-8")).writerow([date, 'Webull Options', round(transactions[date]['amount'],2), round(transactions[date]['fee'],2), round(transactions[date]['interest'],2)])
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
        print('webull market change found')
        splits.append({'amount': -round(marketChange,2), 'account': "Income:Investments:Market Change"})
        for spl in splits:  createdSplits.append(book.createSplit(spl['amount'], spl['account']))
        book.writeTransaction(datetime.today().date(), "Options Market Change", createdSplits)
        if not account.balance:
            account.balance = Decimal(0.00)
        account.updateGnuBalance(account.balance)

def importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(accounts['WebullBrokerageOptions'].gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(WebullActivity), delimiter=','):
        fromAccount = accounts['WebullBrokerageOptions'].gnuAccount
        description = row[1]
        if 'transfer' in description.lower(): 
            continue
        elif 'interest' in description.lower():
            fromAccount = book.getGnuAccountFullName('Interest')
        toAccount = accounts['WebullBrokerageCash'].gnuAccount
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        amount = Decimal(row[2])
        fee = round(Decimal(row[3]),2)
        splits = []
        if fee:
            splits.append({'amount': fee, 'account': book.getGnuAccountFullName('Bank Fees')})
            marketChange = cash = amount
            if len(description) > 11:  # Options transactions
                if amount < 0: # Buy
                    premium = abs(amount)
                    options = abs(amount+fee)
                else:
                    premium = -(amount + fee)
                    options = -(amount)
                splits.append({'amount': premium, 'account': book.getGnuAccountFullName('Premiums')})
                splits.append({'amount': marketChange, 'account':book.getGnuAccountFullName('Market Change')})
                splits.append({'amount': options, 'account': fromAccount})
                splits.append({'amount': cash, 'account': toAccount})
            else: # Stock transactions with fees
                print(f'description: {description}')
                if amount < 0:
                    options = abs(amount + fee)
                else:
                    options = -(amount+fee)
                    cash = cash
                print(f'amount: {amount}, fee: {fee}, options: {options}, cash: {cash}')
                splits.append({'amount': cash, 'account': toAccount})
                splits.append({'amount': options, 'account': fromAccount})
        else: # Stock transactions without fees
            splits.append({'amount': amount, 'account': toAccount})
            splits.append({'amount': -amount, 'account': fromAccount})
        book.writeUniqueTransaction(accounts['WebullBrokerageOptions'], existingTransactions, postDate, description, splits)

def importWebullTransactionsModified(accounts, WebullActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(accounts['WebullBrokerageOptions'].gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(WebullActivity), delimiter=','):
        fromAccount = accounts['WebullBrokerageOptions'].gnuAccount
        description = row[1]
        toAccount = accounts['WebullBrokerageCash'].gnuAccount
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        amount = Decimal(row[2])
        fee = round(Decimal(row[3]),2)
        interest = row[4]
        splits = []
        if fee:
            splits.append({'amount': fee, 'account': book.getGnuAccountFullName('Bank Fees')})
        if interest:
            splits.append({'amount': interest, 'account': book.getGnuAccountFullName('Interest')})
        splits.append({'amount': -amount, 'account': book.getGnuAccountFullName('Premiums')})
        splits.append({'amount': amount, 'account':book.getGnuAccountFullName('Market Change')})
        splits.append({'amount': -amount, 'account': fromAccount})
        splits.append({'amount': amount, 'account': toAccount})
        book.writeUniqueTransaction(accounts['WebullBrokerageOptions'], existingTransactions, postDate, description, splits)        

def runWebullDaily(driver, accounts, book, gnuCashTransactions, dateRange):
    locateWebullWindow(driver)
    getWebullBalance(driver, accounts)
    WebullActivity = captureWebullTransactions(driver, dateRange)
    importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions)
    getWebullOptionsCost(driver, accounts)
    writeWebullOptionMarketChangeTransaction(accounts, book)
    for accountName in list(accounts.keys()): # update balances for ALL
        account = accounts.get(accountName)
        balance = book.getGnuAccountBalance(account.gnuAccount)
        if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
        else:                           account.updateGnuBalance(balance)

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     dateRange = getStartAndEndOfDateRange(timeSpan=7)
#     gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
#     accounts = getWebullAccounts(book)
#     # locateWebullWindow(driver)
#     # getWebullBalance(driver, accounts)
#     WebullActivity = getWebullCSVFile("WebullOptions")
#     importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions)
#     # getWebullOptionsCost(driver, accounts)
#     # writeWebullOptionMarketChangeTransaction(accounts, book)
#     # for accountName in list(accounts.keys()): # update balances for ALL
#     #     account = accounts.get(accountName)
#     #     balance = book.getGnuAccountBalance(account.gnuAccount)
#     #     if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
#     #     else:                           account.updateGnuBalance(balance)
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Test')
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    accounts = getWebullAccounts(book)
    locateWebullWindow(driver)
    # WebullActivity = captureWebullTransactionsModified(driver, dateRange)
    WebullActivity = getWebullCSVFile("WebullOptions")
    importWebullTransactionsModified(accounts, WebullActivity, book, gnuCashTransactions)
    book.closeBook()