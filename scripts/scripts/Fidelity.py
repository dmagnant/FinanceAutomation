import time, csv, json
from datetime import datetime
from decimal import Decimal
from selenium.webdriver.common.by import By

FIDELITY_TX_DEBUG = False

from torch import div

if __name__ == '__main__' or __name__ == "Fidelity":
    from Classes.Asset import USD, Security
    from Classes.GnuCash import GnuCash
    from Classes.Selenium import WebDriver
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP, getKeePassProperties)    
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes, getOTP, getKeePassProperties) 

def getFidelityAccounts(book):
    accounts = {}
    accounts['FidelityIRA'] = USD('FidelityIRA', book)
    accounts['FidelityRothIRA'] = USD('FidelityRothIRA', book)
    accounts['FidelityIndividual'] = USD('FidelityIndividual', book)
    accounts['FidelityBusiness'] = USD('FidelityBusiness', book)
    # accounts['Fidelity401k'] = USD('Fidelity401k', book)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        for child in account.gnuCashAccount.children:
            if child.name == 'Options' or child.name == 'Cash':
                accounts[accountName + child.name] = USD(account.name + child.name, book)
            else:
                accounts[accountName + child.name] = Security(account.name + child.name, book)
    return accounts

def getFidelityBaseAccounts(fidelityAccounts):  return {'FidelityRothIRA':fidelityAccounts['FidelityRothIRA'], 'FidelityIndividual':fidelityAccounts['FidelityIndividual'],'FidelityIRA':fidelityAccounts['FidelityIRA'], 'FidelityBusiness':fidelityAccounts['FidelityBusiness']} #, fidelityAccounts['Fidelity401k']}

def getFidelityCSVFile(account):
    return setDirectory() + rf"\Projects\Coding\Python\FinanceAutomation\Resources\{account}.csv"

def locateFidelityWindow(driver):
    found = driver.findWindowByUrl("digital.fidelity.com")
    if not found:   
        return fidelityLogin(driver)
    else:           
        driver.webDriver.switch_to.window(found)
        return True

def fidelityLogin(driver):
    driver.openNewWindow('https://digital.fidelity.com/prgw/digital/signin/retail')
    num = 1
    while True and num <= 3:
        password = driver.getElement('id', 'dom-pswd-input')
        password.click()
        # password.clear()
        # time.sleep(1)
        # password.send_keys(getPassword('Fidelity'))
        driver.getElementAndClick('xpath', "//*[@id='dom-login-button']/div", wait=2, allowFail=False) # login
        if driver.getElementAndClick('link_text', 'Go back to login', wait=0.1):
            time.sleep(2)
            continue
        if driver.getElementAndSendKeys('id', 'dom-totp-security-code-input', getOTP('Fidelity'), wait=0.1): # otp
            driver.getElementAndClick('xpath', "//*[@id='dom-totp-code-continue-button']/div", wait=0.1) # continue
        num += 1
        break
    if num > 3:
        showMessage("Fidelity Login Failed", "Failed to log in to Fidelity, please check credentials and try again")
        return False
    return True

        
def selectFidelityAccount(driver, account='all'):
    accountNum = str(json.loads(getNotes('Fidelity'))[account]) if account != 'all' else 'allaccounts'
    driver.getElementAndClick('xpath', f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/div[1]/span[2]", wait=0.1) # Account
    driver.webDriver.execute_script("window.scrollTo(0, 0)") #scroll to top of page

def hidePendingTransactions(driver): 
    pendingStatusCellSelector = "pending-table activity-table ag-grid-angular .ag-row .ag-cell span span"
    pendingHeadingXPath = "//span[@slot='heading' and normalize-space()='Pending']"

    if driver.getElement('css_selector', pendingStatusCellSelector, wait=0.3):
        if driver.getElementAndClick('xpath', pendingHeadingXPath, wait=0.3):
            print('Pending transactions section hidden')

def prepFidelityTransactionSearch(driver, formatting=False):
    locateFidelityWindow(driver)
    driver.getElementAndClick('xpath', "//*[@id='portsum-tab-activity']/a/span", wait=0.1) # Activity & Orders
    time.sleep(2)
    if formatting: # the following not necessary when capturing deposits to Fidelity
        driver.getElementAndClick('xpath', "//*[@id='timeperiod-select-button']/span", wait=0.1) #Timeframe
        driver.getElementAndClick('xpath', "//*[@id='60']/s-root/div/label", wait=0.1) # past 60 days
        driver.getElementAndClick('xpath', "//*[@id='timeperiod-select-container']/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper", wait=0.1) # Apply
        hidePendingTransactions(driver)
    time.sleep(1)
    print('Finished preparing Fidelity transaction search')

def getFidelityTransferAccount(driver, sofiAmount, sofiDate):
    selectFidelityAccount(driver, account='all')
    prepFidelityTransactionSearch(driver, formatting=False)
    hidePendingTransactions(driver)
    row = 0
    while True:
        row+=1
        description = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'description', '/div/span/description/div/span'), wait=0.1)
        if not description:
            if row==1:  showMessage('Error finding Description Element', 'Element path for description element has changed, please update. \n' + getFidelityTransactionCellPath(row, 'description', '/div/span/description/div/span'))
            return False
        if "Electronic Funds Transfer Received" in description or "CASH CONTRIBUTION" in description:
            dateElement = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'date'))
            date = datetime.strptime(dateElement, '%b-%d-%Y').date()
            if date == sofiDate:
                amount = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'amount')).replace('$','').replace(',','').replace('-','').replace('+','')
                if sofiAmount == amount:
                    accountName = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'acctNum', '/div/span/account-name/div'))
                    accountPrefix = mapFidelityUIToAccount(accountName)
                    return accountPrefix + 'Cash'

def getFidelityTransactionElementPath(eRow, suffix):
    # Anchor on the history table subtree so row indexing survives page wrapper/id churn.
    tableRoot = (
        "//history-table/activity-table/ag-grid-angular"
        "/div[contains(@class,'ag-root-wrapper')]"
        "/div[contains(@class,'ag-root-wrapper-body')]"
        "/div[contains(@class,'ag-root')]"
        "/div[contains(@class,'ag-body')]"
        "/div[contains(@class,'ag-body-viewport')]"
        "/div[contains(@class,'ag-center-cols-viewport')]/div"
    )
    return f"{tableRoot}/div[{str(eRow)}]{suffix}"

def getFidelityTransactionCellPath(eRow, colId, suffix='/div/span'):
    rowPath = getFidelityTransactionElementPath(eRow, '')
    return f"{rowPath}/div[@role='gridcell' and @col-id='{colId}']{suffix}"

def getFidelityOptionDetailItemPath(eRow, detailRow, valueColumn):
    rowPath = getFidelityTransactionElementPath(eRow, '')
    return (
        f"{rowPath}/div[4]/div/detail-cell/option-details/detail-grid/div/"
        f"text-detail-item[{str(detailRow)}]/div[{str(valueColumn)}]"
    )

def getFidelityStockDetailItemPath(eRow, detailRow, valueColumn):
    rowPath = getFidelityTransactionElementPath(eRow, '')
    return (
        f"{rowPath}/div[4]/div/detail-cell/stock-etf-details/detail-grid/div/"
        f"text-detail-item[{str(detailRow)}]/div[{str(valueColumn)}]"
    )

def getFidelityDetailValueByLabelPath(eRow, label):
    rowPath = getFidelityTransactionElementPath(eRow, '')
    labelLower = label.lower()
    return (
        f"{rowPath}//detail-cell//text-detail-item"
        f"[div[contains(@class,'description-list__term') and "
        f"translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{labelLower}']]"
        f"/div[contains(@class,'description-list__description')]"
    )

def getFidelityExpandedDetailMap(driver):
    details = {}
    try:
        detailCells = driver.webDriver.find_elements(By.CSS_SELECTOR, "detail-cell")
    except Exception:
        return details

    visibleCells = []
    for cell in detailCells:
        try:
            if cell.is_displayed():
                visibleCells.append(cell)
        except Exception:
            continue

    if not visibleCells:
        return details

    targetCell = visibleCells[-1]
    try:
        items = targetCell.find_elements(By.CSS_SELECTOR, "text-detail-item")
    except Exception:
        return details

    for item in items:
        try:
            key = (item.get_attribute("key") or "").strip().lower()
            term = item.find_element(By.CSS_SELECTOR, "div.description-list__term").text.strip().lower()
            value = item.find_element(By.CSS_SELECTOR, "div.description-list__description").text.strip()
            if value:
                if key:
                    details[key] = value
                if term:
                    details[term] = value
        except Exception:
            continue

    return details

def toggleFidelityTransactionDetails(driver, eRow):
    caretButtonPath = getFidelityTransactionCellPath(
        eRow,
        '0',
        "/div/span//button[contains(@aria-label,'Expand transaction details') or contains(@aria-label,'Collapse transaction details')]",
    )
    toggled = driver.getElementAndClick('xpath', caretButtonPath, wait=0.2)
    if toggled:
        time.sleep(0.08)
        if FIDELITY_TX_DEBUG:
            print(f"[Fidelity] row={eRow} toggled detail using caret")
        return True

    if FIDELITY_TX_DEBUG:
        print(f"[Fidelity] row={eRow} failed to toggle detail using caret")
    return False

def getFidelityNextPageSelector():
    return "history-table activity-table ag-grid-angular .ag-paging-panel span.ag-icon.ag-icon-next"

def setFidelityElementPath(eRow, eTable, eColumn):  return getFidelityElementPathRoot() + str(eTable)+']/div['+str(eRow)+']/div/div['+str(eColumn) + ']'

def getFidelityElementPathRoot():   return "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[2]/activity-list[2]/div[2]/div["

def mapFidelityUIToAccount(fidelityAccountNameFromUI):
    if 'ROTH' in fidelityAccountNameFromUI:                    accountPrefix = 'FidelityRothIRA'
    elif 'Individual' in fidelityAccountNameFromUI:            accountPrefix = 'FidelityIndividual'
    elif 'Traditional' in fidelityAccountNameFromUI:           accountPrefix = 'FidelityIRA'
    elif 'Sole Proprietor' in fidelityAccountNameFromUI:       accountPrefix = 'FidelityBusiness'
    elif 'Self-Employed 401k' in fidelityAccountNameFromUI:    accountPrefix = 'Fidelity401k'
    else: accountPrefix = False
    return accountPrefix

def getFidelityBalance(driver, allAccounts, accountBalanceToGet='all'):
    locateFidelityWindow(driver)
    accounts = driver.getElements('css_selector', 'div.acct-selector__acct-title')
    balances = driver.getElements('css_selector', 'div.acct-selector__acct-balance')
    i = 0
    if len(accounts) == len(balances):
        while i < len(accounts):
            accountPrefix = mapFidelityUIToAccount(accounts[i].text)
            if accountPrefix: account = allAccounts[accountPrefix]
            else:   continue
            account.setBalance(balances[i].text.replace('$','').replace(',',''))
            i+=1
    else:
        showMessage('Fidelity Balance issue', f"account name({str(len(accounts))}) and balance({str(len(balances))}) arrays dont match")
    print('Got Fidelity Balances')

def getCurrentValue(driver, row, column):
    value = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{str(row)}]/div[{str(column)}]/div/span", wait=0.1).replace('$', '').replace(',','')
    return Decimal(value)

def getCost(driver, row, column):
    cost = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{str(row)}]/div[{str(column)}]/div/span", wait=0.1).replace('$', '').replace(',','').replace('c','').replace('d','')
    if '--' in cost:    return Decimal(0.00)
    else:               return Decimal(cost)

def getPositionsPageColumnNums(driver):
    fidelityTable = {}
    column = 1
    while True:
        columnName = driver.getElementText('xpath', f'//*[@id="posweb-grid"]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div/div/div[{str(column)}]/div[2]', wait=0.1)
        if not columnName:
            break
        fidelityTable[columnName] = column
        column += 1
    return fidelityTable

def getFidelityPricesSharesAndCost(driver, allAccounts, book, accountToGet='all'):
    locateFidelityWindow(driver)
    accountNum = str(json.loads(getNotes('Fidelity'))[accountToGet]) if accountToGet != 'all' else 'allaccounts'
    if driver.getElementAndClick('xpath', f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div"): # Account
        print('Selected Fidelity Account: ' + accountToGet)
    if driver.getElementAndClick('xpath', "//*[@id='portsum-tab-positions']/a/span"): # Positions
        print('Selected Positions Tab')
    time.sleep(2)
    columnMapping = getPositionsPageColumnNums(driver)
    symbolsWithPricesUpdated = ['GME']
    row = 0
    while True:
        row += 1
        cost = 0
        print(f'row: {row}')
        symbol = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div[{str(row)}]/div/div/span/div/div[2]/button/div/span", wait=0.1)
        print(f'Found symbol: {symbol}')
        if not symbol: # this row lists the account Name
            accountName = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div[{str(row)}]/div/div", wait=0.1)
            if not accountName:
                showMessage('ERROR', 'Error finding the Account name in GetFidelityPricesSharesAndCost')
                break
            print(f'Found account name: {accountName}')
            if accountName == 'Account total':
                row+=1
            elif accountName == 'Grand total':
                break
            else:
                currentAccount = accountName
            continue
        elif row == 1:  showMessage('ERROR', 'Error finding the Account name in GetFidelityPricesSharesAndCost')
        symbol = symbol.replace('$','')
        print(f'Processing symbol: {symbol}')
        accountPrefix = mapFidelityUIToAccount(currentAccount)
        if symbol in ['VXUS', 'VTI', 'Cash', 'GME']:
            account = allAccounts[accountPrefix + symbol]
        elif 'Call' in symbol or 'Put' in symbol or 'GMEWS' in symbol:
            account = allAccounts[accountPrefix + 'Options']
            balance = account.balance + getCurrentValue(driver, row, columnMapping['Current value']) if account.balance else getCurrentValue(driver, row, columnMapping['Current value'])
            account.setBalance(balance)
            cost = account.cost + getCost(driver, row, columnMapping['Cost basis total']) if account.cost else getCost(driver, row, columnMapping['Cost basis total'])
            account.setCost(cost)
            continue
        else:   continue
        if symbol == 'Cash': account.setBalance(getCurrentValue(driver, row, columnMapping['Current value']))
        else: # get equity positions
            price = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{str(row)}]/div[{str(columnMapping['Last price'])}]/div/span", wait=0.1)
            if not price:
                showMessage('Failed to Find Price Info', 'Need to update element information for prices in Fidelity')
            else:
                account.price = Decimal(price.replace('$', ''))
            if symbol not in symbolsWithPricesUpdated:
                book.updatePriceInGnucash(account.symbol, account.price)
                symbolsWithPricesUpdated.append(symbol)
            balance = driver.getElementText('xpath', f"//*[@id='posweb-grid']/div/div[3]/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[{str(row)}]/div[{str(columnMapping['Quantity'])}]/div/span/div/span", wait=0.1)
            if not balance:
                showMessage('Failed to Find Balance Info', 'Need to update element information for balances in Fidelity')
            else:
                balance = float(balance.replace('$', '').replace(',',''))
                balance = balance if not account.balance else balance + account.balance
            value = float(getCurrentValue(driver, row, columnMapping['Current value']))
            value = value if not account.value else value + account.value
            cost = float(getCost(driver,row,columnMapping['Cost basis total']))
            cost = cost if not account.cost else cost + account.cost
            account.setBalance(balance)
            account.setCost(cost)
            account.setValue(value)
    print('Got Fidelity Prices, Shares and Cost')

def captureFidelityTransactions(driver, dateRange, account='all'):
    locateFidelityWindow(driver)
    selectFidelityAccount(driver, account)
    fidelityActivity = getFidelityCSVFile(account)
    open(fidelityActivity, 'w', newline='').truncate()
    hidePendingTransactions(driver)
    driver.randomSleep(0.6, 1.2)
    row = 0
    while True:
        transactionStartTime = datetime.now()
        row += 1
        accountName = account
        dateElement = driver.getElement('xpath', getFidelityTransactionCellPath(row, 'date'))
        if not dateElement:
            if row == 1:
                showMessage('Error finding Date Element', 'Element path for date element has changed, please update. \n' + getFidelityTransactionCellPath(row, 'date'))
                break
            elif not driver.getElementAndClick('css_selector', getFidelityNextPageSelector(), wait=0.2):
                break
            row = 0
            continue

        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date >= dateRange['startDate']:
            amount = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'amount')).replace('$','').replace(',','').replace('-','').replace('+','')
            if not amount:
                continue
            descriptionElement = driver.getElement('xpath', getFidelityTransactionCellPath(row, 'description', '/div/span/description/div/span'), wait=0.1)
            description = descriptionElement.text
            fees = 0
            if "CASH CONTRIBUTION" in description or "Electronic Funds Transfer" in description or "REINVESTMENT" in description or "JOURNAL" in description or "EXPIRED" in description or "ASSIGNED as of" in description or "TRANSFER OF ASSETS" in description or "DISTRIBUTION" in description:
                continue
            elif "YOU BOUGHT" in description.upper() or "YOU SOLD" in description.upper():
                expanded = toggleFidelityTransactionDetails(driver, row)
                if not expanded:
                    descriptionElement.click()
                    time.sleep(0.08)
                if FIDELITY_TX_DEBUG:
                    print(f"[Fidelity] processing trade row={row} description={description}")

                detailValues = {}
                for _ in range(2):
                    detailValues = getFidelityExpandedDetailMap(driver)
                    if detailValues:
                        break
                    time.sleep(0.05)

                commissionValue = detailValues.get('commission', False)
                feesValue = detailValues.get('fees', False)
                if commissionValue and commissionValue != 'Not available':
                    fees += Decimal(commissionValue.replace('$','').replace(',',''))
                if feesValue and feesValue != 'Not available':
                    fees += Decimal(feesValue.replace('$','').replace(',',''))

                if 'ASSIGNED' in description.upper() or "TRANSACTION" not in description.upper():
                    sharesText = detailValues.get('shares', False)
                    if not sharesText:
                        sharesText = detailValues.get('quantity', False)
                    if not sharesText:
                        sharesText = detailValues.get('contracts', False)
                    if sharesText and sharesText != 'Not available':
                        shares = sharesText.replace('+','').replace(',','').replace('−', '-').strip()
                        if FIDELITY_TX_DEBUG:
                            print(f"[Fidelity] row={row} parsed sharesText={sharesText} -> shares={shares}")
                    else:
                        # Some stock trades do not show share count in detail; keep processing with amount fallback.
                        shares = amount
                        if FIDELITY_TX_DEBUG:
                            print(f"[Fidelity] row={row} no share-like label found; fallback shares=amount={amount}")
                else:
                    shares = amount
                    if FIDELITY_TX_DEBUG:
                        print(f"[Fidelity] row={row} option transaction branch; shares=amount={amount}")
                if expanded:
                    toggleFidelityTransactionDetails(driver, row)
                else:
                    descriptionElement.click()
            else:
                shares = amount

            if account == 'all':
                accountName = driver.getElementText('xpath', getFidelityTransactionCellPath(row, 'acctNum', '/div/span/account-name/div'))
                accountName = mapFidelityUIToAccount(accountName)

            transaction = date, description, amount, shares, accountName, fees
            csv.writer(open(fidelityActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
            transactionEndTime = datetime.now()
            print('transaction with description: ' + description + ' took: ' + str(transactionEndTime - transactionStartTime) + ' to process')
        else:
            break
    return fidelityActivity

def formatFidelityOptionTransactionDescription(rawDescription, accountName):
    print(f'Raw Description: {rawDescription}, Account Name: {accountName}')
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
        modifiedDescription = modifiedDescription.replace('GAMESTOP CORPOR 100GME+10GMEWS ','').replace('GAMESTOP CORPOR 100GME+10GMEWS','').replace('GAMESTOP CORPORA 100GME+10GMEWS ', '')
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
    optionsAccounts = [accounts['FidelityRothIRAOptions'], accounts['FidelityIndividualOptions'], accounts['FidelityIRAOptions'], accounts['FidelityBusinessOptions']]
    marketChange = 0
    for account in optionsAccounts:
        if not account.balance: account.balance = 0
        gnuBalance = book.getGnuAccountBalance(account.gnuAccount)
        account.updateGnuBalance(gnuBalance)
        change = Decimal(account.balance) - account.gnuBalance
        if change:
            splits.append({'amount': change, 'account': account.gnuAccount})
            marketChange += change
    if marketChange:
        splits.append({'amount': -marketChange, 'account': book.getGnuAccountFullName("Market Change")})
        for spl in splits:  createdSplits.append(book.createSplit(spl['amount'], spl['account']))
        book.writeTransaction(datetime.today().date(), "Options Market Change", createdSplits)
        for account in optionsAccounts:
            if not account.balance:
                account.balance = Decimal(0.00)
            account.updateGnuBalance(account.balance)
    print('Wrote Fidelity Options Market Change Transaction')

def importFidelityTransactions(account, fidelityActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccountIncludingChildren(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(fidelityActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1] # determine fromAccount based on raw description
        description = rawDescription
        amount = Decimal(row[2])
        shares = Decimal(row[3])
        accountinTrans = row[4]
        fees = round(Decimal(row[5]),2)
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        splits = []
        if "REINVESTMENT" in rawDescription or "REF #T" in rawDescription or 'TRANSFERRED' in rawDescription:
            continue
        elif "DIVIDEND" in rawDescription:
            amount,shares = -amount,-shares
            fromAccount += ":Cash"
            description = accountinTrans + " Dividend"
            if 'IRA' in accountinTrans:
                toAccount = book.getGnuAccountFullName('Dividends')
            elif 'FZFXX' in rawDescription:
                toAccount = book.getGnuAccountFullName('FZFXX Business Dividend') if 'Business' in accountinTrans else book.getGnuAccountFullName('FZFXX Personal Dividend')
            elif 'SPAXX' in rawDescription:
                toAccount = book.getGnuAccountFullName('SPAXX Dividend')
        elif "MARGIN INTEREST" in rawDescription:
            fromAccount += ":Cash"  
            description = accountinTrans + " Margin Interest"
            toAccount = book.getGnuAccountFullName('Bank Fees')
        elif "OPENING TRANSACTION" in rawDescription or "CLOSING TRANSACTION" in rawDescription:
            fromAccount = "Income:Investments:Premiums"
            description = formatFidelityOptionTransactionDescription(rawDescription, accountinTrans)
            if "YOU BOUGHT" in rawDescription:
                amount,shares = -amount,-shares
        elif "YOU BOUGHT" in rawDescription: 
            description = accountinTrans + " Investment"
            amount,shares = -amount,-shares
        elif "YOU SOLD" in rawDescription:
            if float(amount)>1 and float(shares)<1:
                shares = -shares
            description = accountinTrans + " Sale"
        if "VXUS" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:           fromAccount += ":VXUS"
        elif "VTI" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:          fromAccount += ":VTI"                                     
        elif "GME" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:          fromAccount += ":GME"
        elif "VOO" in rawDescription and "DIVIDEND" not in rawDescription and "TRANSACTION" not in rawDescription:          fromAccount += ":VOO"
        if toAccount == book.getGnuAccountFullName('Other'):
            if "FidelityIndividual" in description:            
                toAccount = book.getGnuAccountFullName('FidelityIndividualCash')
            elif "FidelityRothIRA" in description:              
                toAccount = book.getGnuAccountFullName('FidelityRothIRACash')
            elif "FidelityIRA" in description:                  
                toAccount = book.getGnuAccountFullName('FidelityIRACash')
            elif "FidelityBusiness" in description:        
                toAccount = book.getGnuAccountFullName('FidelityBusinessCash')
        if not shares: shares = amount
        if fees:
            if 'Cash' in toAccount:
                splits.append({'amount': amount, 'account': toAccount, 'quantity': amount})
            else:
                splits.append({'amount': amount, 'account': toAccount, 'quantity': shares})
            splits.append({'amount':fees, 'account': book.getGnuAccountFullName('Bank Fees')})
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
        else: # buy/sell shares 
            splits.append({'amount':amount, 'account':toAccount, 'quantity':round(Decimal(amount),2)})
            splits.append({'amount':-amount, 'account':fromAccount, 'quantity':-round(Decimal(shares),2)})
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)
    print('Imported Fidelity Transactions for ' + account.name)

def runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange):
    if not locateFidelityWindow(driver):
        print('failed to login to Fidelity')
        return False
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


if __name__ == '__main__':
    driver = WebDriver("Chrome")
    book = GnuCash('Finance')
    startTime = datetime.now()
    print('starting script at ' + str(startTime))

    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    accounts = getFidelityAccounts(book)

    # runFidelityDaily(driver, accounts, book, gnuCashTransactions, dateRange)

    locateFidelityWindow(driver)
    # getFidelityBalance(driver, accounts)
    # prepFidelityTransactionSearch(driver, True)
    # baseAccounts = getFidelityBaseAccounts(accounts)
    # for accountName in list(baseAccounts.keys()): # get transactions per account (x3)
    #     account = baseAccounts.get(accountName)
    #     fidelityActivity = captureFidelityTransactions(driver, dateRange, accountName)
    # getFidelityBalance(driver, accounts)
    prepFidelityTransactionSearch(driver, True)
    baseAccounts = getFidelityBaseAccounts(accounts)
    for accountName in list(baseAccounts.keys()): # get transactions per account (x3)
        account = baseAccounts.get(accountName)
        fidelityActivity = captureFidelityTransactions(driver, dateRange, accountName)
        # importFidelityTransactions(account, fidelityActivity, book, gnuCashTransactions)

    book.closeBook()
    endTime = datetime.now()
    print('finished script at ' + str(endTime))
    print('script took this long: ' + str(endTime - startTime))