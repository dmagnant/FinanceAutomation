import time, csv, json
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

if __name__ == '__main__' or __name__ == "Fidelity":
    from Classes.Asset import USD, Security
    from Classes.GnuCash import GnuCash, createNewTestBook
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes)    
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash, createNewTestBook
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes)    

def getFidelityAccounts(book):
    accounts = {}
    accounts['IRA'] = USD('IRA', book)
    accounts['rIRA'] = USD('Roth IRA', book)
    accounts['Brokerage'] = USD('Brokerage', book)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        for child in account.gnuCashAccount.children:
            if child.name == 'Options' or child.name == 'SPAXX':
                accounts[accountName + child.name] = USD(account.name + ' ' + child.name, book)                
            else:
                accounts[accountName + child.name] = Security(account.name + ' ' + child.name, book)                
    return accounts

def getFidelityBaseAccounts(fidelityAccounts):  return {'rIRA':fidelityAccounts['rIRA'], 'Brokerage':fidelityAccounts['Brokerage'],'IRA':fidelityAccounts['IRA']}

def getFidelityCSVFile(account):
    accountSuffix = f"fidelity{account}"
    return setDirectory() + f"\Projects\Coding\Python\FinanceAutomation\Resources\{accountSuffix}.csv"

def locateFidelityWindow(driver):
    found = driver.findWindowByUrl("digital.fidelity.com")
    if not found:   fidelityLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def fidelityLogin(driver):
    driver.openNewWindow('https://digital.fidelity.com/prgw/digital/login/full-page')
    driver.webDriver.refresh()
    time.sleep(1)
    # driver.webDriver.find_element(By.ID,'password').send_keys(getPassword('Fidelity')) # pre-filled
    time.sleep(2)
    driver.webDriver.find_element(By.XPATH,"//*[@id='dom-login-button']/div").click() # login

def selectFidelityAccount(driver, account='all'):
    accountNum = str(json.loads(getNotes('Fidelity'))[account]) if account != 'all' else 'allaccounts'
    try:    driver.clickXPATHElementOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/div[1]/span[2]") # Account2]
    except ElementClickInterceptedException:    exception = "already on all accounts"
    driver.webDriver.execute_script("window.scrollTo(0, 0)") #scroll to top of page
    
def clickHistoryButton(driver): 
    while True:
        driver.clickXPATHElementOnceAvailable("//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[1]/div[2]/apex-kit-field-group/s-root/div/div/s-slot/s-assigned-wrapper/div/core-filter-button[2]/pvd3-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # History
        if driver.getXPATHElementOnceAvailable("//*[@id='ao-pending-table']/s-root/button/div/span/s-slot/s-assigned-wrapper/span") == False:
            break
               
def prepFidelityTransactionSearch(driver, formatting=False):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-activity']/a/span").click() # Activity & Orders
    if formatting: # the following not necessary when capturing deposits to Fidelity
        driver.clickXPATHElementOnceAvailable("//*[@id='timeperiod-select-button']/span[1]") #Timeframe
        driver.clickXPATHElementOnceAvailable("//*[@id='60']/s-root/div/label") # past 60 days
        driver.clickXPATHElementOnceAvailable("//*[@id='timeperiod-select-container']/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # Apply
        clickHistoryButton(driver)
    time.sleep(1)

def getFidelityTransferAccount(driver, sofiAmount, sofiDate):
    prepFidelityTransactionSearch(driver, formatting=False)
    row, table = 0, 2
    while True:
        row+=1
        column = 2
        try:    dateElement = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column))
        except NoSuchElementException:
            if row==1:  showMessage('Error finding Date Element', 'Element path for date element has changed, please update. \n' + setFidelityElementPath(row, table, column))
            break
        if not (dateElement.text and row == 1): # Pending transactions still visible
            clickHistoryButton(driver)
        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date == sofiDate:
            column+=1
            accountName = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)).text
            if 'ROTH' in accountName:           accountName = 'rIRA'
            elif 'Individual' in accountName:   accountName = 'Brokerage'
            elif 'Traditional' in accountName:  accountName = 'IRA'
            column+=1
            descriptionElement = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)+'/div')
            description = descriptionElement.text
            if "Electronic Funds Transfer Received" in description or "CASH CONTRIBUTION" in description:
                column+=1
                amount = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)).text.replace('$','').replace(',','').replace('-','').replace('+','')
                if sofiAmount == amount:
                    return accountName
    
def setFidelityElementPath(eRow, eTable, eColumn):  return getFidelityElementPathRoot() + str(eTable)+']/div['+str(eRow)+']/div/div['+str(eColumn) + ']'

def getFidelityElementPathRoot():   return "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[2]/activity-list[2]/div[2]/div["

def getFidelityBalance(driver, allAccounts, accountBalanceToGet='all'):
    locateFidelityWindow(driver)
    # accountsToUpdate = ['Brokerage', 'IRA', 'rIRA'] if accountBalanceToGet == 'all' else [accountBalanceToGet]
    accountsToUpdate = list(getFidelityBaseAccounts(allAccounts).keys()) if accountBalanceToGet == 'all' else [accountBalanceToGet]
    accountNums = json.loads(getNotes('Fidelity'))
    for account in accountsToUpdate:
        accountNum = str(accountNums[account])
        balance = driver.getXPATHElementTextOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").replace('$','').replace(',','')
        allAccounts[account].setBalance(balance)

def getCurrentValue(driver, row): 
    value = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',','')
    return Decimal(value)

def getCost(driver, row):
    cost = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[11]/div/span").text.replace('$', '').replace(',','').replace('c','')
    if '--' in cost:    
        return Decimal(0.00)
    else:               return Decimal(cost)

def getFidelityPricesSharesAndCost(driver, allAccounts, book, accountToGet='all'):
    locateFidelityWindow(driver)
    accountNum = str(json.loads(getNotes('Fidelity'))[accountToGet]) if accountToGet != 'all' else 'allaccounts'
    driver.clickXPATHElementOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div") # Account
    driver.clickXPATHElementOnceAvailable("//*[@id='portsum-tab-positions']/a/span") # Positions
    driver.webDriver.implicitly_wait(1)
    row = 0
    while True:
        row += 1
        cost = 0
        try:    
            accountName = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/h3").text
        except  NoSuchElementException:
            try:
                symbol = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/div/button").text.replace('$','')
                if symbol == 'VXUS':
                    if 'ROTH' in accountName:           account = allAccounts['rIRAVXUS']
                elif symbol == 'VTI':
                    if 'ROTH' in accountName:           account = allAccounts['rIRAVTI']
                    elif 'Individual' in accountName:   account = allAccounts['BrokerageVTI']
                    elif 'Traditional' in accountName:  account = allAccounts['IRAVTI']
                elif symbol == 'Cash':
                    if 'ROTH' in accountName:           account = allAccounts['rIRASPAXX']
                    elif 'Individual' in accountName:   account = allAccounts['BrokerageSPAXX']
                    elif 'Traditional' in accountName:  account = allAccounts['IRASPAXX'] 
                elif symbol == 'GME':
                    if 'ROTH' in accountName:           account = allAccounts['rIRAGME']
                    elif 'Individual' in accountName:   account = allAccounts['BrokerageGME']
                    elif 'Traditional' in accountName:  account = allAccounts['IRAGME']
                elif 'Call' in symbol or 'Put' in symbol:
                    if 'ROTH' in accountName:           account = allAccounts['rIRAOptions']
                    elif "Individual" in accountName:   account = allAccounts['BrokerageOptions']
                    elif 'Traditional' in accountName:  account = allAccounts['IRAOptions']
                    balance = account.balance + getCurrentValue(driver, row) if account.balance else getCurrentValue(driver, row)
                    account.setBalance(balance)
                    cost = account.cost + getCost(driver, row) if account.cost else getCost(driver, row)
                    account.setCost(cost)
                    continue
                else:   continue
                if symbol == 'Cash': account.setBalance(getCurrentValue(driver, row))
                else: # get equity positions
                    account.price = Decimal(driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[1]/div/span").text.replace('$', ''))
                    book.updatePriceInGnucash(account.symbol, account.price)
                    account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[9]/div/span").text.replace('$', '').replace(',',''))                    
                    account.value = getCurrentValue(driver, row)
                    cost = getCost(driver, row)
                    if cost:
                        account.setCost(cost)
            except NoSuchElementException:
                if accountToGet != 'all':
                    if row==2:  showMessage('Failed to Find Individual Account Share/Price Info', 'Need to update element information for prices and shares in Fidelity')
                    break
                try:
                    if 'Account Total' == driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/div/p").text:
                        row+=1
                except NoSuchElementException:
                    if row==1:  showMessage('Failed to Find Share Info', 'Need to update element information for prices and shares in Fidelity')
                    break

def captureFidelityTransactions(driver, dateRange, account='all'):
    locateFidelityWindow(driver)
    selectFidelityAccount(driver, account)
    fidelityActivity = getFidelityCSVFile(account)
    open(fidelityActivity, 'w', newline='').truncate()
    row, table = 0, 2
    while True:
        row+=1
        column, accountName = 2, account
        try:    dateElement = driver.getXPATHElementOnceAvailable(setFidelityElementPath(row, table, column))
        except NoSuchElementException:
            if row==1:  showMessage('Error finding Date Element', 'Element path for date element has changed, please update.')
            else: 
                try: driver.clickXPATHElementOnceAvailable("//*[@id='ao-history-list']/div[3]/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # load more results
                except NoSuchElementException:  break
        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date >= dateRange['startDate'] and date <= dateRange['endDate']:
            column+=1
            if account == 'all':
                accountName = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)).text
                if 'ROTH' in accountName:           accountName = 'rIRA'
                elif 'Individual' in accountName:   accountName = 'Brokerage'
                elif 'Traditional' in accountName:  accountName = 'IRA'
                column+=1
            descriptionElement = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)+'/div')
            description = descriptionElement.text
            fees = 0
            column+=1
            amount = driver.webDriver.find_element(By.XPATH,setFidelityElementPath(row, table, column)).text.replace('$','').replace(',','').replace('+','')
            if not amount:  continue
            if "CASH CONTRIBUTION" in description or "Electronic Funds Transfer" in description or "REINVESTMENT" in description or "JOURNAL" in description or "EXPIRED" in description or "ASSIGNED as of" in description: continue
            elif "YOU BOUGHT" in description.upper() or "YOU SOLD" in description.upper(): # buy/sell shares or options
                descriptionElement.click()
                feesNum = 15
                while feesNum < 19:
                    feeDescription = driver.webDriver.find_element(By.XPATH, getFidelityElementPathRoot()+str(table)+']/div['+str(row)+']/div[2]/div/activity-order-detail-panel/div/div/div['+str(feesNum)+']').text
                    if feeDescription == "Fees" or feeDescription == "Commission": # fees
                        feesNum+=1
                        fees += Decimal(driver.webDriver.find_element(By.XPATH,getFidelityElementPathRoot()+str(table)+']/div['+str(row)+']/div[2]/div/activity-order-detail-panel/div/div/div['+str(feesNum)+']').text.replace('$',''))
                        feesNum+=1
                    else: feesNum=19
                if "TRANSACTION" not in description.upper(): # shares bought
                    shares = driver.webDriver.find_element(By.XPATH,getFidelityElementPathRoot()+str(table)+']/div['+str(row)+']/div[2]/div/activity-order-detail-panel/div/div/div[10]').text.replace('+','')
                else: shares = amount # options bought
                descriptionElement.click()
            else:   shares = amount
            transaction = date, description, amount, shares, accountName, fees
            csv.writer(open(fidelityActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        else:  break
    return fidelityActivity

def formatFidelityOptionTransactionDescription(rawDescription, accountName):
    modifiedDescription = rawDescription
    finalDescription = ''
    if "BOUGHT" in rawDescription:
        finalDescription += 'Bought '
    elif 'SOLD' in rawDescription:  
        finalDescription += 'Sold '
    modifiedDescription = modifiedDescription.replace('YOU BOUGHT ','').replace('YOU SOLD ','')
    modifiedDescription = modifiedDescription.replace('OPENING TRANSACTION ','').replace('CLOSING TRANSACTION ','')

    if 'GME' in rawDescription:     finalDescription += 'GME '
    else:                           finalDescription += 'Unknown Security '
    modifiedDescription = modifiedDescription.replace('(GME) GAMESTOP CORPORATION ','').replace('(GME) GAMESTOP CORPORATION','')

    if "CALL" in rawDescription:    finalDescription += 'Call '
    elif 'PUT' in rawDescription:   finalDescription += 'Put '
    modifiedDescription = modifiedDescription.replace('CALL ','').replace('PUT ','')

    finalDescription += '@ ' + modifiedDescription[modifiedDescription.index('$'):modifiedDescription.index('$')+5].replace(' ','').replace('(','')
    finalDescription += ' expiring ' + datetime.strptime(modifiedDescription[:9], '%b %d %y').date().strftime('%m/%d/%y')
    return accountName + ' ' + finalDescription

def writeFidelityOptionMarketChangeTransaction(accounts, book):
    splits, createdSplits=[], []
    marketChange = 0
    for account in [accounts['rIRAOptions'], accounts['BrokerageOptions'], accounts['IRAOptions']]:
        account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
        change = Decimal(account.balance) - account.gnuBalance
        splits.append({'amount': change, 'account': account.gnuAccount})
        marketChange += change
    splits.append({'amount': -marketChange, 'account': "Income:Investments:Market Change"})
    for spl in splits:  createdSplits.append(book.createSplit(spl['amount'], spl['account']))
    book.writeTransaction(datetime.today().date(), "Options Market Change", createdSplits)

def importFidelityTransactions(account, fidelityActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(fidelityActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1] # determine fromAccount based on raw description
        amount = Decimal(row[2])
        shares = Decimal(row[3])
        accountinTrans = row[4]
        fees = round(Decimal(row[5]),2)
        fromAccount = account.gnuAccount
        splits = []
        if "REINVESTMENT" in rawDescription or "REF #T" in rawDescription:
            continue
        elif "DIVIDEND" in rawDescription:
            amount,shares = -amount,-shares
            fromAccount += ":SPAXX"
            description = accountinTrans + " Dividend"
        elif "MARGIN INTEREST" in rawDescription: 
            fromAccount += ":SPAXX"  
            description = accountinTrans + " Margin Interest"
        elif "OPENING TRANSACTION" in rawDescription or "CLOSING TRANSACTION" in rawDescription:
            fromAccount = "Income:Investments:Premiums"
            description = formatFidelityOptionTransactionDescription(rawDescription, accountinTrans)
        elif "YOU BOUGHT" in rawDescription: 
            shares = -shares
            description = accountinTrans + " Investment"
        elif "YOU SOLD" in rawDescription:
            if float(amount)>1 and float(shares)<1:
                shares = -shares
            description = accountinTrans + " Sale"
        if "VXUS" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:           fromAccount += ":VXUS"
        elif "VTI" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:          fromAccount += ":VTI"                                     
        elif "GME" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:          fromAccount += ":GME"
        toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        if not shares: shares = amount
        if fees:
            splits.append({'amount': amount, 'account': toAccount, 'quantity': shares})
            splits.append({'amount':fees, 'account':"Expenses:Bank Fees"})
            if fromAccount == 'Income:Investments:Premiums': # buy/sell options
                splits.append({'amount':-(amount+fees), 'account': fromAccount, 'quantity':-round(Decimal(amount+fees),2)})
                splits.append({'amount':-amount, 'account':account.gnuAccount + ":Options"})
                splits.append({'amount':amount, 'account':'Income:Investments:Market Change'})
            else: # sell shares
                splits.append({'amount':-(amount+fees), 'account':fromAccount, 'quantity':-round(Decimal(shares),2)})
        elif "Margin Interest" in description:
            splits.append({'amount':amount, 'account':fromAccount, 'quantity':shares})
            splits.append({'amount':-amount, 'account':toAccount, 'quantity':-round(Decimal(shares),2)})
        else: # dividends # buy/sell shares 
            splits.append({'amount':amount, 'account':toAccount, 'quantity':round(Decimal(amount),2)})
            splits.append({'amount':-amount, 'account':fromAccount, 'quantity':-round(Decimal(shares),2)})
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

def runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange):
    locateFidelityWindow(driver)
    getFidelityBalance(driver, accounts)
    getFidelityPricesSharesAndCost(driver, accounts, book)
    prepFidelityTransactionSearch(driver, True)
    baseAccounts = getFidelityBaseAccounts(accounts)
    for accountName in list(baseAccounts.keys()): # get transactions per account (x3)
        account = baseAccounts.get(accountName)
        fidelityActivity = captureFidelityTransactions(driver, dateRange, accountName)
        importFidelityTransactions(account, fidelityActivity, book, gnuCashTransactions)
    writeFidelityOptionMarketChangeTransaction(accounts, book)
    for accountName in list(accounts.keys()): # update balances for ALL
        account = accounts.get(accountName)
        balance = book.getGnuAccountBalance(account.gnuAccount)
        if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
        else:                           account.updateGnuBalance(balance)


# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Test')
#     dateRange = getStartAndEndOfDateRange(timeSpan=20)
#     gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
#     accounts = getFidelityAccounts(book)
#     runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange)
#     book.closeBook()

if __name__ == '__main__':
    book = GnuCash('Finance')
    print("ORIGINAL")
    print(getFidelityAccounts(book))
    print("REVISED VERSION: ")
    print(getFidelityAccounts(book))
