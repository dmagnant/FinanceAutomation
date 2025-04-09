import time, csv, json
from datetime import datetime, timedelta

from decimal import Decimal

from selenium.webdriver import ActionChains
from selenium.webdriver import Keys


if __name__ == '__main__' or __name__ == "Webull":
    from Classes.Asset import USD
    from Classes.GnuCash import GnuCash
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP)    
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP)    

def unlockTrading(driver):
    if driver.getElementAndClick('partial_link_text', 'unlock', wait=2):
        # time.sleep(2)
        driver.getElementAndSendKeys('xpath', '/html/body', str(json.loads(getNotes('Webull'))['TradingPassword']), wait=2)

def getWebullAccounts(book):
    accounts = {}
    accounts['WebullBrokerage'] = USD('WebullBrokerage', book)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        for child in account.gnuCashAccount.children:
            if child.name == 'Options' or child.name == 'Cash':
                accounts[accountName + child.name] = USD(account.name + child.name, book)
    return accounts

def getWebullCSVFile(name=''):
    return setDirectory() + rf"\Projects\Coding\Python\FinanceAutomation\Resources\Webull{name}.csv"

def webullClosePopUps(driver):
    driver.getElementAndClick('xpath', '/html/body/div[5]/div/div/div[1]/button/svg', wait=1) # close 
    driver.getElementAndClick('xpath', '/html/body/div[4]/svg', wait=1) # close
    
def locateWebullWindow(driver):
    found = driver.findWindowByUrl("app.webull.com/account")
    if not found:   webullLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    webullClosePopUps(driver)

def webullLogin(driver):
    driver.openNewWindow('https://www.webull.com')
    login = driver.getElementAndClick('xpath', '/html/body/div/section/header/div/div[2]/div/button[2]', wait=2) # login
    if login:
        time.sleep(1)
        # driver.getElementAndSendKeys('xpath', '/html/body/div[1]/div/div[2]/div/div/div[5]/div[1]/div[2]/div/div/span/input', os.environ.get('Phone')) # enter phone as user
        driver.getElementAndSendKeys('xpath', '/html/body/div[1]/div/div[2]/div/div/div[5]/div[3]/div/span/input',getPassword('Webull')) # enter password
        driver.getElementAndClick('xpath', '/html/body/div[1]/div/div[2]/div/div/div[5]/div[4]/button/span') # Log In
        if driver.getElement('xpath', '/html/body/div[1]/div/div[2]/div/div/div/div/div[1]/div/div/input'): # 2FA Code
            showMessage('Enter 2FA Code', 'Enter Code Manually, then click OK here')
            driver.getElementAndClick('xpath', '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/button') # Next
    driver.webDriver.get('https://app.webull.com/account')
    unlockTrading(driver)

def getWebullBalanceByPath(driver, path):
    balance = driver.getElementText('xpath', path)
    if balance:
        balance = float(balance.replace(',',''))
    return balance

def getWebullBalance(driver, accounts):
    locateWebullWindow(driver)
    unlockTrading(driver)
    accounts['WebullBrokerage'].balance = getWebullBalanceByPath(driver, "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[1]/div/div[2]/div[1]/div[2]/span")
    if not accounts['WebullBrokerage'].balance:
        showMessage('Failed to find balance', 'No balance found for ' + accounts['WebullBrokerage'].name)
    accounts['WebullBrokerageCash'].balance = getWebullBalanceByPath(driver, "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[1]/div/div[3]/div[3]/div/div/div[1]/div[2]/div/div/div/div/div/div[3]/div/div[2]/span")                                
    if not accounts['WebullBrokerageCash'].balance:
        showMessage('Failed to find balance', 'No balance found for ' + accounts['WebullBrokerageCash'].name)    
    accounts['WebullBrokerageOptions'].balance = round(accounts['WebullBrokerage'].balance - accounts['WebullBrokerageCash'].balance,2)

def getWebullOptionsCost(driver, allAccounts, accountToGet='all'):
    locateWebullWindow(driver)
    unlockTrading(driver)
    costTotal = 0
    row = 2
    driver.getElementAndClick('xpath', "//*[@id='tabs_lv2_0']/span") # Positions
    driver.getElementText('xpath', "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[1]") # My Positions
    while True:
        costAmount = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[8]")
        if costAmount != False:
            costTotal += float(costAmount)
            row+=1
        else:
            break
    allAccounts['WebullBrokerageOptions'].cost = costTotal

def parseWebullADDescription(rawDescription):
    if ('Bought' in rawDescription or 'Sold' in rawDescription):
        if '.000' not in rawDescription:
            currentYear = str(datetime.today().date().year)
            previousYear = str(datetime.today().date().year - 1)
            if currentYear in rawDescription or previousYear in rawDescription:
                return False # skip options contracts missing price (likely from today/last business day, and will be formatted correctly next business day)
    description = rawDescription.replace('Bought ', '').replace('Sold ', '').replace('.000', '')
    if len(description) > 5 and 'Interest' not in description and 'dividend' not in description.lower():  # further parsing for options transactions
        spaceAfterSymbol = description.find(' ')
        side = ''
        if spaceAfterSymbol != -1 and spaceAfterSymbol + 8 < len(description):
            description = description[:spaceAfterSymbol + 1] + description[spaceAfterSymbol + 9:] # remove date
            if 'C' in description[spaceAfterSymbol + 1:]:
                side = 'Call'
            elif 'P' in description[spaceAfterSymbol + 1:]:
                side = 'Put'
            description = description.replace(' C ', ' $').replace(' P ', ' $')
            if side:    description += f' {side}'
    return description

def getFromAccountDetailsPage(driver, dateRange):
    accountDetailsCSV = getWebullCSVFile('AD')
    open(accountDetailsCSV, 'w', newline='').truncate()
    accountDetailsLink = driver.getElementAndClick('xpath', "//*[@id='tabs_lv2_1']/span") # Account Details
    if accountDetailsLink == False:
        showMessage('Error', 'Account Details button not found')
        return
    driver.getElementAndClick('xpath', '/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/span/div/span', wait=2) # Date Range
    driver.getElementAndClick('xpath', '/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[2]/span', wait=2) # 1M timeframe
    webullClosePopUps(driver)
    adRow = 1
    while True:
        adRow+=1
        adRawDateTime = driver.getElementTextAndLocate('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[3]/span") # Date
        if adRawDateTime:
            adDateTime = datetime.strptime(adRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
            ahDate = adDateTime.strftime('%Y-%m-%d')
            if adDateTime.date() >= dateRange['startDate'] and adDateTime.date() <= dateRange['endDate']:
                amount = float(driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[4]").replace('+','').replace(',','')) # Amount
                rawDescription = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(adRow)}]/td[2]") # Description
                description = parseWebullADDescription(rawDescription)
                if description:
                    csv.writer(open(accountDetailsCSV, 'a', newline='', encoding="utf-8")).writerow([ahDate, description, round(amount,2)])
            else:   break # no more transactions in date range
        else:       break # no more transactions or error finding date
    rows = list(csv.reader(open(accountDetailsCSV), delimiter=','))
    consolidatedRows = []
    descriptions = []
    num = 1
    for row in rows:
        rowIsConsolidated = False
        if num == 1:
            consolidatedRows.append(row)
            descriptions.append(row[1])
            num+=1
        else:
            if row[1] in descriptions:
                for consolidatedRow in consolidatedRows:
                    if consolidatedRow[1] == row[1] and consolidatedRow[0] == row[0]:
                        rowIsConsolidated = True
                        consolidatedRow[2] = round(float(consolidatedRow[2]) + float(row[2]), 2)
                        break
            else:   descriptions.append(row[1])
            if not rowIsConsolidated: consolidatedRows.append(row) # Description same, but different date
    csv.writer(open(accountDetailsCSV, 'w', newline='')).writerows(consolidatedRows)
    return accountDetailsCSV

def parseWebullOHDescription(description):
    def find_second_space(description):
        first_space = description.find(' ')
        if first_space == -1:
            return -1  # No space found
        second_space = description.find(' ', first_space + 1)
        return second_space
    index = find_second_space(description)
    if index < 0 or index >= len(description):
        return description
    optionType = 'Call' if 'Call' in description else 'Put'
    return f'{description[:index]} {optionType}'

def parseWebullAmount(quantity, averagePrice, side, description):
    if 'Call' in description or 'Put' in description: 
        quantity *= 100
    if side == 'Buy':   
        averagePrice *= -1
    return round(quantity * averagePrice, 2)

def getFromOrderHistoryPage(driver, dateRange):
    orderHistory = getWebullCSVFile('OH')
    open(orderHistory, 'w', newline='').truncate()
    row = 1
    actionChains = ActionChains(driver.webDriver)
    dayOfWeek = datetime.today().date().weekday()
    # check Positions > Order History for fees and description
    driver.getElementAndClick('xpath', "//*[@id='tabs_lv2_0']/span") # Positions
    if not driver.getElementAndClick('xpath', "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div[3]"): # Order History
        showMessage('Error', 'Order History button not found')
    driver.getElementAndClick('xpath', "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/div[1]/span/div/span") # timeframe
    orderFilledTab = driver.getElement('xpath', "/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[2]") # Order Filled
    action_chains = ActionChains(driver.webDriver)
    action_chains.move_to_element(orderFilledTab).send_keys(Keys.RIGHT).perform()
    if dayOfWeek == 0: # if Monday, select 1M timeframe to be able to capture Friday transactions
        time.sleep(0.5)
        action_chains.send_keys(Keys.DOWN).perform()
    time.sleep(0.5)
    action_chains.send_keys(Keys.SPACE).perform() 
    webullClosePopUps(driver)
    while True:
        row+=1
        print(f'Row: {row}')
        ohRawDateTime = driver.getElementTextAndLocate('xpath',f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[9]", wait=2) # filled time
        if ohRawDateTime == False:
            break
        elif ohRawDateTime != '':   
            ohDateTime = datetime.strptime(ohRawDateTime[:-4], '%m/%d/%Y %H:%M:%S') # remove timezone
            print(ohDateTime)
            ohDate = ohDateTime.strftime('%Y-%m-%d')
        else:
            continue
        if ohDateTime.date() == datetime.today().date() or (dayOfWeek == 4 and datetime.today().date() in [ohDateTime.date() + timedelta(days=i) for i in range(3)]):
            continue # skip current days transaction, and skip friday transaction until Monday
        elif ohDateTime.date() >= dateRange['startDate'] and ohDateTime.date() <= dateRange['endDate']:
            print(f'Processing {ohRawDateTime}')
            rawDescription = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[2]", wait=2) # Symbol
            side = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[3]", wait=2) # Side (buy/sell)
            quantity = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[8]", wait=2) # Filled Quantity
            description = parseWebullOHDescription(rawDescription)
            averagePrice = driver.getElementText('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[10]", wait=2) # Average Price
            amount = parseWebullAmount(float(quantity), float(averagePrice), side, description)
            actionChains.context_click(driver.getElement('xpath', f"/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[3]/div/div/div/div[1]/div[2]/div/div/div/div/table/tbody/tr[{str(row)}]/td[3]")).perform() # right-click on row
            time.sleep(1)
            driver.getElementAndClick('xpath', "/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[1]") # Order Details
            odRow = 5
            while True:
                fee = 0
                odRow+=1
                feeDescription = driver.getElementText('xpath', f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[1]", wait=1)
                if feeDescription:
                    if feeDescription == 'Transaction Fee':
                        feeText = driver.getElementText('xpath', f"/html/body/div[5]/div[2]/div/div[{str(odRow)}]/div[2]", wait=1).replace('$', '')
                        if feeText != '--':
                            fee = round(float(feeText), 2)
                            break
                    elif feeDescription == 'Order Status':
                        odRow+=1 # skip extra row which is divider between order status and transaction fee
                else:   break
            driver.getElementAndSendKeys('xpath', '/html/body', Keys.ESCAPE) # close pop-up window
            if fee == 0:
                print(f'Fee not found for {description} on {ohDateTime}')
            csv.writer(open(orderHistory, 'a', newline='', encoding="utf-8")).writerow([ohDate, description, amount, fee])

    rows = list(csv.reader(open(orderHistory), delimiter=','))
    consolidatedRows = []
    descriptions = []
    num = 1
    for row in rows:
        rowIsConsolidated = False
        if row[3] == 0:
            row.append('fee not found')
        if num == 1:
            consolidatedRows.append(row)
            descriptions.append(row[1])
            num+=1
        else:
            if row[1] in descriptions:
                for consolidatedRow in consolidatedRows:
                    if consolidatedRow[1] == row[1] and consolidatedRow[0] == row[0]:
                        rowIsConsolidated = True
                        consolidatedRow[2] = round(float(consolidatedRow[2]) + float(row[2]), 2)
                        consolidatedRow[3] = round(float(consolidatedRow[3]) + float(row[3]),2)
                        break
            else:   descriptions.append(row[1])
            if not rowIsConsolidated: consolidatedRows.append(row) # Description same, but different date
    csv.writer(open(orderHistory, 'w', newline='')).writerows(consolidatedRows)
    return orderHistory

def captureWebullTransactions(driver, dateRange):
    locateWebullWindow(driver)
    WebullActivity = getWebullCSVFile()
    open(WebullActivity, 'w', newline='').truncate()
    # accountDetailsTransactions = getWebullCSVFile('AD')
    # orderHistoryTransactions = getWebullCSVFile('OH')
    accountDetailsTransactions = getFromAccountDetailsPage(driver, dateRange)
    orderHistoryTransactions = getFromOrderHistoryPage(driver, dateRange) 
    accountDetails = list(csv.reader(open(accountDetailsTransactions), delimiter=','))
    orderHistory = list(csv.reader(open(orderHistoryTransactions), delimiter=','))
    for oh in orderHistory:
        ohAmount = float(oh[2])
        fee = float(oh[3])
        ADspecificTransactions = []
        for ad in accountDetails:
            if 'Interest' in ad[1] or 'dividend' in ad[1].lower():
                ad.append(0)
                csv.writer(open(WebullActivity, 'a', newline='')).writerow(ad)
                ADspecificTransactions.append(ad)
            adAmount = float(ad[2])
            if ad[0] == oh[0] and ad[1] == oh[1]:
                ohAmountNet = ohAmount - fee
                if ohAmountNet != adAmount:
                    oh[2] = round(adAmount + fee, 2)
                csv.writer(open(WebullActivity, 'a', newline='')).writerow(oh)
                break
        for ad in ADspecificTransactions:
            accountDetails.remove(ad)
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
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(accounts['WebullBrokerageCash'].gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(WebullActivity), delimiter=','):
        fromAccount = accounts['WebullBrokerageCash'].gnuAccount
        description = row[1]
        if 'Interest' in description:
            toAccount = book.getGnuAccountFullName('Interest')
        elif 'dividend' in description.lower():
            toAccount = book.getGnuAccountFullName('Dividends')
        elif 'Put' in description or 'Call' in description:
            toAccount = book.getGnuAccountFullName('Premiums')
        else:
            toAccount = book.getGnuAccountFullName('WebullBrokerageOptions')
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        fromAmount = amount = Decimal(row[2])
        fee = round(Decimal(row[3]),2)
        splits = []
        if fee:
            splits.append({'amount': fee, 'account': book.getGnuAccountFullName('Bank Fees')})
            fromAmount = amount - fee
        splits.append({'amount': fromAmount, 'account': fromAccount})
        splits.append({'amount': -amount, 'account': toAccount})
        book.writeUniqueTransaction(accounts['WebullBrokerageCash'], existingTransactions, postDate, description, splits)

def getWebullDuplicateTransactions(account, book, dateRange):
    gnuCashTransactions = book.getTransactionsByGnuAccountAndDateRange(account, dateRange)

    transaction_counts = {}

    # Iterate through the transactions
    for tr in gnuCashTransactions:
        key = f"{tr.post_date} {tr.description}"  # Combine post_date and description as a unique key
        if key in transaction_counts:
            transaction_counts[key] += 1  # Increment count if the key already exists
        else:
            transaction_counts[key] = 1  # Initialize count for new keys

    for key, count in transaction_counts.items():
        if count > 1:  # Check if the transaction appears more than once

            # Look through Webull.csv for matching transactions
            webull_csv_path = getWebullCSVFile()  # Path to Webull.csv
            with open(webull_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    # Combine date and description from the CSV row
                    csv_key = f"{row[0]} {row[1]}"  # Assuming row[0] is the date and row[1] is the description
                    if csv_key == key:
                        print(f"{key} is duplicated. Fee captured right now is: {row[3]}")
                        break

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
    getWebullDuplicateTransactions(accounts['WebullBrokerageCash'].gnuAccount, book, dateRange)

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
    # book = GnuCash('Finance')
    # accounts = getWebullAccounts(book)
    dateRange = getStartAndEndOfDateRange(timeSpan=5)
    locateWebullWindow(driver)
    # WebullActivity = captureWebullTransactions(driver, dateRange)
    # accountDetailsTransactions = getFromAccountDetailsPage(driver, dateRange)
    # orderHistoryTransactions = getFromOrderHistoryPage(driver, dateRange) 
    # gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    # WebullActivity = getWebullCSVFile()
    # gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    # importWebullTransactions(accounts, WebullActivity, book, gnuCashTransactions)
    # getWebullDuplicateTransactions(accounts['WebullBrokerageCash'].gnuAccount, book, dateRange)

    # book.closeBook()
    driver.getElementAndClick('xpath', "/html/body/div[1]/main/section/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div[2]/div[1]/div[1]/span/div/span") # timeframe
    orderFilledTab = driver.getElement('xpath', "/html/body/div[4]/div/div/div/div[1]/div[2]/div/div/div/button[2]") # Order Filled
    
    # Use ActionChains to send RIGHT, RIGHT, SPACE
    action_chains = ActionChains(driver.webDriver)
    action_chains.move_to_element(orderFilledTab).send_keys(Keys.RIGHT).perform()
    time.sleep(0.5)
    action_chains.send_keys(Keys.DOWN).perform()
    time.sleep(0.5)
    action_chains.send_keys(Keys.SPACE).perform() 