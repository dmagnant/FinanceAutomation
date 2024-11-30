import time, csv, json
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

if __name__ == '__main__' or __name__ == "Fidelity":
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

def getFidelityAccounts(book):
    accounts = {}
    accounts['FidelityIRA'] = USD('FidelityIRA', book)
    accounts['FidelityRothIRA'] = USD('FidelityRothIRA', book)
    accounts['FidelityBrokerage'] = USD('FidelityBrokerage', book)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        for child in account.gnuCashAccount.children:
            if child.name == 'Options' or child.name == 'SPAXX':
                accounts[accountName + child.name] = USD(account.name + child.name, book)
            else:
                accounts[accountName + child.name] = Security(account.name + child.name, book)
    return accounts

def getFidelityBaseAccounts(fidelityAccounts):  return {'FidelityRothIRA':fidelityAccounts['FidelityRothIRA'], 'FidelityBrokerage':fidelityAccounts['FidelityBrokerage'],'FidelityIRA':fidelityAccounts['FidelityIRA']}

def getFidelityCSVFile(account):
    accountSuffix = f"fidelity{account}"
    return setDirectory() + rf"\Projects\Coding\Python\FinanceAutomation\Resources\{accountSuffix}.csv"

def locateFidelityWindow(driver):
    found = driver.findWindowByUrl("digital.fidelity.com")
    if not found:   fidelityLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def fidelityLogin(driver):
    driver.openNewWindow('https://digital.fidelity.com/prgw/digital/login/full-page')
    driver.webDriver.refresh()
    time.sleep(1)
    # driver.webDriver.find_element(By.ID,'dom-pswd-input').send_keys(getPassword('Fidelity')) # pre-filled
    time.sleep(2)
    driver.webDriver.find_element(By.XPATH,"//*[@id='dom-login-button']/div").click() # login
    otpElement = driver.getIDElementOnceAvailable("dom-totp-security-code-input")
    if otpElement:
        otpElement.send_keys(getOTP('Fidelity'))
        driver.clickXPATHElementOnceAvailable("//*[@id='dom-totp-code-continue-button']/div") # continue
def selectFidelityAccount(driver, account='all'):
    accountNum = str(json.loads(getNotes('Fidelity'))[account]) if account != 'all' else 'allaccounts'
    try:    driver.clickXPATHElementOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/div[1]/span[2]") # Account
    except ElementClickInterceptedException:    exception = "already on all accounts"
    driver.webDriver.execute_script("window.scrollTo(0, 0)") #scroll to top of page
    
def clickHistoryButton(driver): 
    if driver.getXPATHElementOnceAvailable("//*[@id='ao-pending-table']/s-root/button/div/span/s-slot/s-assigned-wrapper/span") != False:
        driver.clickXPATHElementOnceAvailable("//*[@id='accountDetails']/div/div/div[2]/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/section/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[1]/div[2]/apex-kit-field-group/s-root/div/div/s-slot/s-assigned-wrapper/div/core-filter-button[2]/pvd3-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # History

def prepFidelityTransactionSearch(driver, formatting=False):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-activity']/a/span").click() # Activity & Orders
    if formatting: # the following not necessary when capturing deposits to Fidelity
        driver.clickXPATHElementOnceAvailable("//*[@id='timeperiod-select-button']/span") #Timeframe
        driver.clickXPATHElementOnceAvailable("//*[@id='60']/s-root/div/label") # past 60 days
        driver.clickXPATHElementOnceAvailable("//*[@id='timeperiod-select-container']/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # Apply
        clickHistoryButton(driver)
    time.sleep(1)

def getFidelityTransferAccount(driver, sofiAmount, sofiDate):
    selectFidelityAccount(driver, account='all')
    prepFidelityTransactionSearch(driver, formatting=False)
    clickHistoryButton(driver)
    row = 0
    while True:
        row+=1
        try:
            description = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row, '/div[4]/div/div')).text
        except NoSuchElementException:
            if row==1:  showMessage('Error finding Description Element', 'Element path for description element has changed, please update. \n' + getFidelityTransactionElementPath(row,"/div[4]/div/div"))
            break
        if "Electronic Funds Transfer Received" in description or "CASH CONTRIBUTION" in description:
            dateElement = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,"/div[2]")).text
            date = datetime.strptime(dateElement, '%b-%d-%Y').date()
            if date == sofiDate:
                amount = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'/div[5]')).text.replace('$','').replace(',','').replace('-','').replace('+','')
                if sofiAmount == amount:
                    accountName = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'/div[3]/span/span')).text
                    if 'ROTH' in accountName:           return 'FidelityRothIRA'
                    elif 'Individual' in accountName:   return 'FidelityBrokerage'
                    elif 'Traditional' in accountName:  return 'FidelityIRA'

def getFidelityTransactionElementPath(eRow, suffix):    return f"//*[@id='ao-history-list']/div[2]/div[{str(eRow)}]/div{suffix}"

def setFidelityElementPath(eRow, eTable, eColumn):  return getFidelityElementPathRoot() + str(eTable)+']/div['+str(eRow)+']/div/div['+str(eColumn) + ']'

def getFidelityElementPathRoot():   return "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[2]/activity-list[2]/div[2]/div["

def getFidelityBalance(driver, allAccounts, accountBalanceToGet='all'):
    locateFidelityWindow(driver)
    accounts = driver.webDriver.find_elements(By.CSS_SELECTOR,'div.acct-selector__acct-title')
    balances = driver.webDriver.find_elements(By.CSS_SELECTOR,'div.acct-selector__acct-balance')
    i = 0
    if len(accounts) == len(balances):
        while i < len(accounts):
            if 'ROTH' in accounts[i].text:           account = allAccounts['FidelityRothIRA']
            elif 'Individual' in accounts[i].text:   account = allAccounts['FidelityBrokerage']
            elif 'Traditional' in accounts[i].text:  account = allAccounts['FidelityIRA']
            account.setBalance(balances[i].text.replace('$','').replace(',',''))
            print(f'set balance for {accounts[i].text} to: {str(balances[i].text)}')
            i+=1
    else:
        showMessage('Fidelity Balance issue', f"account name({str(len(accounts))}) and balance({str(len(balances))}) arrays dont match")
    
def getCurrentValue(driver, row): 
    value = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',','')
    return Decimal(value)

def getCost(driver, row):
    cost = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[11]/div/span").text.replace('$', '').replace(',','').replace('c','')
    if '--' in cost:    
        return Decimal(0.00)
    else:               return Decimal(cost)

def getFidelityPricesSharesAndCost(driver, allAccounts, book, accountToGet='all'):
    locateFidelityWindow(driver)
    accountNum = str(json.loads(getNotes('Fidelity'))[accountToGet]) if accountToGet != 'all' else 'allaccounts'
    driver.clickXPATHElementOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/span") # Account
    driver.clickXPATHElementOnceAvailable("//*[@id='portsum-tab-positions']/a/span") # Positions
    driver.webDriver.implicitly_wait(1)
    row = 0
    while True:
        row += 1
        cost = 0
        try:    
            accountName = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/h3").text         
        except  NoSuchElementException:
            try:
                symbol = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/button/div/span").text.replace('$','')
                if symbol == 'VXUS':
                    if 'ROTH' in accountName:           account = allAccounts['FidelityRothIRAVXUS']
                elif symbol == 'VTI':
                    if 'ROTH' in accountName:           account = allAccounts['FidelityRothIRAVTI']
                    elif 'Individual' in accountName:   account = allAccounts['FidelityBrokerageVTI']
                    elif 'Traditional' in accountName:  account = allAccounts['FidelityIRAVTI']
                elif symbol == 'Cash':
                    if 'ROTH' in accountName:           account = allAccounts['FidelityRothIRASPAXX']
                    elif 'Individual' in accountName:   account = allAccounts['FidelityBrokerageSPAXX']
                    elif 'Traditional' in accountName:  account = allAccounts['FidelityIRASPAXX'] 
                elif symbol == 'GME':
                    if 'ROTH' in accountName:           account = allAccounts['FidelityRothIRAGME']
                    elif 'Individual' in accountName:   account = allAccounts['FidelityBrokerageGME']
                    elif 'Traditional' in accountName:  account = allAccounts['FidelityIRAGME']
                elif 'Call' in symbol or 'Put' in symbol:
                    if 'ROTH' in accountName:           account = allAccounts['FidelityRothIRAOptions']
                    elif "Individual" in accountName:   account = allAccounts['FidelityBrokerageOptions']
                    elif 'Traditional' in accountName:  account = allAccounts['FidelityIRAOptions']
                    balance = account.balance + getCurrentValue(driver, row) if account.balance else getCurrentValue(driver, row)
                    account.setBalance(balance)
                    cost = account.cost + getCost(driver, row) if account.cost else getCost(driver, row)
                    account.setCost(cost)
                    continue
                else:   continue
                if symbol == 'Cash': account.setBalance(getCurrentValue(driver, row))
                else: # get equity positions
                    account.price = Decimal(driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[1]/div/span").text.replace('$', ''))
                    book.updatePriceInGnucash(account.symbol, account.price)
                    account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[9]/div/span").text.replace('$', '').replace(',',''))
                    account.value = getCurrentValue(driver, row)
                    cost = getCost(driver, row)
                    if cost:
                        account.setCost(cost)
            except NoSuchElementException:
                if accountToGet != 'all':
                    if row==2:  showMessage('Failed to Find Individual Account Share/Price Info', 'Need to update element information for prices and shares in Fidelity')
                    break
                else:
                    if row==2:
                        print('skipping security lending message')
                        continue
                try:
                    if 'Account Total' == driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/div/p").text:
                        row+=1
                except NoSuchElementException:
                    if row==1:  
                        showMessage('Failed to Find Share Info', 'Need to update element information for prices and shares in Fidelity')
                    break

def captureFidelityTransactions(driver, dateRange, account='all'):
    locateFidelityWindow(driver)
    selectFidelityAccount(driver, account)
    fidelityActivity = getFidelityCSVFile(account)
    open(fidelityActivity, 'w', newline='').truncate()
    row = 0
    while True:
        row+=1
        accountName = account
        try:    dateElement = driver.getXPATHElementOnceAvailable(getFidelityTransactionElementPath(row,"/div[2]"))
        except NoSuchElementException:
            if row==1:  showMessage('Error finding Date Element', 'Element path for date element has changed, please update. \n' + getFidelityTransactionElementPath(row,"/div[2]"))
            else: 
                try: driver.clickXPATHElementOnceAvailable("//*[@id='ao-history-list']/div[3]/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # load more results
                except NoSuchElementException:  break
        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date >= dateRange['startDate'] and date <= dateRange['endDate']:
            amount = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'/div[4]')).text.replace('$','').replace(',','').replace('-','').replace('+','')
            if not amount:  continue
            descriptionElement = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row, '/div[3]/div/div'))
            description = descriptionElement.text
            fees = 0
            if "CASH CONTRIBUTION" in description or "Electronic Funds Transfer" in description or "REINVESTMENT" in description or "JOURNAL" in description or "EXPIRED" in description or "ASSIGNED as of" in description: continue
            elif "YOU BOUGHT" in description.upper() or "YOU SOLD" in description.upper(): # buy/sell shares or options
                descriptionElement.click()
                feesNum = 15
                while feesNum < 19:
                    feeDescription = driver.webDriver.find_element(By.XPATH, getFidelityTransactionElementPath(row,'[2]/div/activity-order-detail-panel/div/div/div[')+f'{str(feesNum)}]').text
                    if feeDescription == "Fees" or feeDescription == "Commission": # fees
                        feesNum+=1
                        fees += Decimal(driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'[2]/div/activity-order-detail-panel/div/div/div[')+f'{str(feesNum)}]').text.replace('$',''))
                        feesNum+=1
                    else: feesNum=19
                if "TRANSACTION" not in description.upper(): # shares bought
                    shares = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'[2]/div/activity-order-detail-panel/div/div/div[10]')).text.replace('+','')
                else: shares = amount # options bought
                descriptionElement.click()
            else:   shares = amount
            if account == 'all':
                accountName = driver.webDriver.find_element(By.XPATH,getFidelityTransactionElementPath(row,'/div[3]/span/span')).text
                if 'ROTH' in accountName:           accountName = 'FidelityRothIRA'
                elif 'Individual' in accountName:   accountName = 'FidelityBrokerage'
                elif 'Traditional' in accountName:  accountName = 'FidelityIRA'
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
    if 'GME' in rawDescription:     
        finalDescription += 'GME '
        modifiedDescription = modifiedDescription.replace('(GME) GAMESTOP CORPORATION ','').replace('(GME) GAMESTOP CORPORATION','')
    elif 'VXUS' in rawDescription:
        finalDescription += 'VXUS '
        modifiedDescription = modifiedDescription.replace('(VXUS) VANGUARD TOTAL ','').replace('(VXUS) VANGUARD TOTAL','')
    else:                           finalDescription += 'Unknown Security '
    if "CALL" in rawDescription:    finalDescription += 'Call '
    elif 'PUT' in rawDescription:   finalDescription += 'Put '
    modifiedDescription = modifiedDescription.replace('CALL ','').replace('PUT ','')

    finalDescription += '@ ' + modifiedDescription[modifiedDescription.index('$'):modifiedDescription.index('$')+5].replace(' ','').replace('(','')
    finalDescription += ' expiring ' + datetime.strptime(modifiedDescription[:9], '%b %d %y').date().strftime('%m/%d/%y')
    return accountName + ' ' + finalDescription

def writeFidelityOptionMarketChangeTransaction(accounts, book):
    splits, createdSplits=[], []
    optionsAccounts = [accounts['FidelityRothIRAOptions'], accounts['FidelityBrokerageOptions'], accounts['FidelityIRAOptions']]
    marketChange = 0
    for account in optionsAccounts:
        if account.balance:
            print(f'balance of {account.name} is {str(account.balance)}')
            gnuBalance = book.getGnuAccountBalance(account.gnuAccount)
            print(f'pre-change gnubalance for {account.name} is {str(gnuBalance)}')
            account.updateGnuBalance(gnuBalance)
            change = Decimal(account.balance) - account.gnuBalance
            if change:
                splits.append({'amount': change, 'account': account.gnuAccount})
                marketChange += change
    if marketChange:
        splits.append({'amount': -marketChange, 'account': "Income:Investments:Market Change"})
        for spl in splits:  createdSplits.append(book.createSplit(spl['amount'], spl['account']))
        book.writeTransaction(datetime.today().date(), "Options Market Change", createdSplits)
        for account in optionsAccounts:
            print(f'new gnubalance for {account.name} is {account.balance}')
            if not account.balance:
                account.balance = Decimal(0.00)
            account.updateGnuBalance(account.balance)

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
            if "YOU BOUGHT" in rawDescription:
                amount,shares = -amount,-shares
        elif "YOU BOUGHT" in rawDescription: 
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
            if 'SPAXX' in toAccount:
                splits.append({'amount': amount, 'account': toAccount, 'quantity': amount})
            else:
                splits.append({'amount': amount, 'account': toAccount, 'quantity': shares})
            splits.append({'amount':fees, 'account':"Expenses:Bank Fees"})
            if fromAccount == 'Income:Investments:Premiums': # buy/sell options
                if 'YOU SOLD CLOSING TRANSACTION' in rawDescription:
                    splits.append({'amount':-(amount+fees), 'account': account.gnuAccount + ":Options", 'quantity':-round(Decimal(amount+fees),2)})
                    splits.append({'amount':-amount, 'account':fromAccount})
                else: 
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
    prepFidelityTransactionSearch(driver, True)
    baseAccounts = getFidelityBaseAccounts(accounts)
    for accountName in list(baseAccounts.keys()): # get transactions per account (x3)
        account = baseAccounts.get(accountName)
        fidelityActivity = captureFidelityTransactions(driver, dateRange, accountName)
        importFidelityTransactions(account, fidelityActivity, book, gnuCashTransactions)
    getFidelityPricesSharesAndCost(driver, accounts, book)
    writeFidelityOptionMarketChangeTransaction(accounts, book)
    for accountName in list(accounts.keys()): # update balances for ALL
        account = accounts.get(accountName)
        balance = book.getGnuAccountBalance(account.gnuAccount)
        if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
        else:                           account.updateGnuBalance(balance)
        print(f'new gnubalance for {account.name} is {book.getGnuAccountBalance(account.gnuAccount)}')


# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     dateRange = getStartAndEndOfDateRange(timeSpan=20)
#     gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
#     accounts = getFidelityAccounts(book)
#     runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange)
#     book.closeBook()


# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     accounts = getFidelityAccounts(book)
#     dateRange = getStartAndEndOfDateRange(timeSpan=20)
#     locateFidelityWindow(driver)
#     prepFidelityTransactionSearch(driver, True)
#     baseAccounts = getFidelityBaseAccounts(accounts)
#     for accountName in list(baseAccounts.keys()): # get transactions per account (x3)
#         account = baseAccounts.get(accountName)
#         print(f'account is {str(accountName)}')
#         if accountName == 'FidelityBrokerage':
#             print('starting search')
#             fidelityActivity = captureFidelityTransactions(driver, dateRange, accountName)  

if __name__ == '__main__':
    driver = Driver("Chrome")
    Finances = Spreadsheet('Finances', 'Investments', driver)

            