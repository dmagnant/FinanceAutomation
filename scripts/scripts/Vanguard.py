import time, csv, json
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Vanguard":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, showMessage, setDirectory, getNotes)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange,
                                             getUsername, showMessage, setDirectory, getNotes)

def getVanguardAccounts(book):
    return {'V401k': USD("401k", book), 'TSM401k': Security("Total Stock Market", book), '401kCash':USD('NM Asset Fund', book), 'EBI': Security("Employee Benefit Index", book)}

def vanguardLogin(driver):
    driver.openNewWindow('https://logon.vanguard.com/logon?site=pi')
    # driver.webDriver.find_element(By.ID, "USER").send_keys(getUsername('Vanguard'))
    time.sleep(2)
    # driver.webDriver.find_element(By.ID, "PASSWORD-blocked").send_keys(getPassword('Vanguard'))
    if 'ownyourfuture' not in driver.webDriver.current_url: # check if already logged in
        driver.clickXPATHElementOnceAvailable("//*[@id='username-password-submit-btn-1']/span") # log in
        try:     # handle security code
            driver.webDriver.find_element(By.ID, 'CODE')
            showMessage('Security Code', "Enter Security code, then click OK")
            driver.webDriver.find_element(By.XPATH,"//*[@id='radioGroupId-bind-selection-group']/c11n-radio[1]/label/div").click() # remember me
            driver.webDriver.find_element(By.XPATH, "//*[@id='security-code-submit-btn']/button/span/span").click() # verify
        except NoSuchElementException:  exception = "caught"
    driver.webDriver.get('https://retirementplans.vanguard.com/VGApp/pe/web/sc/pso-pex-secure-overview-webapp/home')

def locateVanguardWindow(driver):
    found = driver.findWindowByUrl("retirementplans.vanguard.com")
    if not found:   found = driver.findWindowByUrl("ownyourfuture.vanguard.com")
    if not found:   vanguardLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    
def getVanguard401kPriceSharesAndCost(driver, account, book, planId):
    locateVanguardWindow(driver)
    driver.webDriver.get('https://retirementplans.vanguard.com/VGApp/pe/faces/Investments.xhtml?SelectedPlanId=' + planId)
    row = 2
    while True:
        try:
            fundNum = driver.getXPATHElementTextOnceAvailable(getVanguardBalanceTableElement(row, 'td[1]'))
        except NoSuchElementException:
            break
        if hasattr(account, 'symbol') and fundNum==account.symbol:
            account.balance = driver.getXPATHElementTextOnceAvailable(getVanguardBalanceTableElement(row, 'td[3]')).replace(',','')
            account.price = driver.webDriver.find_element(By.XPATH, getVanguardBalanceTableElement(row, 'td[4]')).text.replace('$', '')
            book.updatePriceInGnucash(account.symbol, Decimal(account.price))
            account.value = driver.webDriver.find_element(By.XPATH,getVanguardBalanceTableElement(row, 'td[5]')).text.replace('$','',).replace(',','')
            driver.webDriver.get('https://retirementplans.vanguard.com/VGApp/pe/faces/PersonalPerformance.xhtml?SelectedPlanId=' + planId)
            account.cost = driver.getXPATHElementTextOnceAvailable("//*[@id='planDetailmyPerformanceForm:dataTabBox:accountActivityNetCashFlowRowSinceInception']/td[2]").replace('$','',).replace(',','')
            break
        elif account.name == 'NM Asset Fund' and fundNum == '4769':
            account.balance = driver.getXPATHElementTextOnceAvailable(getVanguardBalanceTableElement(row, 'td[3]')).replace(',','')
            break
        row+=1

def getVanguardBalanceTableElement(row, suffix):
    return f"//*[@id='investmentsForm:allFundsTabletbody0']/tr[{str(row)}]/{suffix}"

def captureVanguard401kTransactions(driver, planId, lastMonth):
    locateVanguardWindow(driver)
    driver.webDriver.get('https://retirementplans.vanguard.com/VGApp/pe/faces/TransactionHistory.xhtml?SelectedPlanId=' + planId)
    v401kActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\401k.csv"
    open(v401kActivity, 'w', newline='').truncate()
    driver.clickXPATHElementOnceAvailable("//*[@id='TransactionHistoryTabBox_tabBoxItemLink0']/span/h2") # Transactions
    driver.clickIDElementOnceAvailable("TransactionHistoryTabBox:transHistoryForm:viewByDate_main") # View history from: option:
    driver.clickIDElementOnceAvailable("TransactionHistoryTabBox:transHistoryForm:viewByDate:historyItemLabel2") # View last 3 months to ensure all transactions are visible
    time.sleep(1)
    row, transactionTable = 1, "//*[@id='TransactionHistoryTabBox:transHistoryForm:transactionHistoryDataTabletbody0']/tr["
    while True:
        column=1
        row+=1
        try:    date = datetime.strptime(driver.webDriver.find_element(By.XPATH,(transactionTable + str(row) + "]/td[" + str(column) + "]")).text, '%m/%d/%Y').date()
        except NoSuchElementException:
            if row<=2:  showMessage('unable to find date', 'Likely need to adjust element path')
            break
        description = ''
        if date.month == lastMonth['endDate'].month:
            column+=1
            description = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text # transaction description
            column+=1
            description +=" "+ driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text # fund name
            column+=1
            shares = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text
            column+=2
            amount = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text.replace('$','').replace(',','')
            amount = -float(amount) if "Fee" in description else amount
            shares = -float(shares) if "Fee" in description else shares
            transaction = date, description, shares, amount
            csv.writer(open(v401kActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month < lastMonth['endDate'].month or date.year < lastMonth['endDate'].year:  break
    return v401kActivity

def importVanguardTransactions(account, vanguardActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(vanguardActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1]
        description = rawDescription
        shares = round(Decimal(row[2]),3)
        amount = Decimal(row[3])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        splits = []
        if 'NM Annual Fixed Rate Fund' in rawDescription:           
            continue
        elif "Plan Contribution" in rawDescription:                  
            description = "401k Investment"
            toAccount = book.getGnuAccountFullName('Vanguard401k')
        elif "Dividend" in rawDescription:                          
            description = "401k Dividend"
            toAccount = book.getGnuAccountFullName('Dividends')
        elif "Fee" in rawDescription:                               
            description = "401k Fee"
            toAccount = book.getGnuAccountFullName('Bank Fees')
        elif "Fund to Fund Out" in rawDescription:                  
            description = "401k Transfer Out"
            shares = -shares
            amount = -amount
        elif "Fund to Fund In" in rawDescription:                  
            description = "401k Transfer In"
        # toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        if not shares: shares = amount
        splits.append({'amount': -amount, 'account': toAccount})
        splits.append({'amount': amount, 'account': fromAccount, 'quantity': shares})
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

def runVanguardPension(driver, accounts, book):
    locateVanguardWindow(driver)
    today, interestYTD = datetime.today().date(), getVanguardBalancesAndPensionInterestYTD(driver, accounts)
    writePensionTransaction(book, today, accounts['Pension'], interestYTD)
    accounts['Pension'].updateGnuBalance(book.getBalance(accounts['Pension'].gnuAccount))

def getVanguardBalancesAndPensionInterestYTD(driver, accounts):
    locateVanguardWindow(driver)
    driver.webDriver.get('https://ownyourfuture.vanguard.com/main/dashboard/assets-details')
    accounts['Pension'].setBalance(driver.getXPATHElementTextOnceAvailable('/html/body/vg-vgn-nav/main/div[2]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[3]/div/app-details-card/div/div/div[1]/div[3]/h4').replace('$','').replace(',',''))
    return driver.getXPATHElementTextOnceAvailable("/html/body/vg-vgn-nav/main/div[2]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[4]/div/app-details-card/div/div/div[1]/div[3]/h4").replace('$','').replace(',','')

def writePensionTransaction(book, today, account, interestYTD):
    lastMonth, interestAmount = getStartAndEndOfDateRange(today, "month"), 0
    transactions = [tr for tr in book.readBook.transactions
                    if str(tr.post_date.strftime('%Y')) == str(lastMonth['startDate'].year)
                    for spl in tr.splits
                    if spl.account.fullname == account.gnuAccount]
    for tr in transactions:
        for spl in tr.splits:
            if spl.account.fullname == "Income:Investments:Interest":   interestAmount = interestAmount + abs(spl.value)
    print('account balance: ' + str(account.balance))
    print('account gnu balance: ' + str(account.gnuBalance))
    accountChange = Decimal(account.balance) - account.gnuBalance
    interest = Decimal(interestYTD) - interestAmount
    splits = []
    splits.append({'amount': -interest, 'account': book.getGnuAccountFullName('Interest')})
    splits.append({'amount': -(accountChange - interest), 'account': book.getGnuAccountFullName('Pension Contributions')})
    splits.append({'amount': accountChange, 'account': account.gnuAccount})
    book.writeTransaction(lastMonth['endDate'], 'Contribution + Interest', splits)

def writeAssetFundTransaction(book, account, change, lastMonth):
    splits = []
    splits.append({'amount': -change, 'account': book.getGnuAccountFullName('Interest')})
    splits.append({'amount': change, 'account': account.gnuAccount})
    book.writeTransaction(lastMonth['endDate'], 'NM Asset Fund Interest', splits)
    
def runVanguard401k(driver, accounts, book, gnuCashTransactions, lastMonth):
    locateVanguardWindow(driver)
    planIDs = json.loads(getNotes('Vanguard'))
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        if hasattr(account, 'symbol'):
            planID = str(planIDs[accountName])
            getVanguard401kPriceSharesAndCost(driver, account, book, planID)
            v401kActivity = captureVanguard401kTransactions(driver, planID, lastMonth)
            importVanguardTransactions(account, v401kActivity, book, gnuCashTransactions)
            account.updateGnuBalanceAndValue(book.getGnuAccountBalance(account.gnuAccount))
        else:
            if accountName == '401kCash': 
                getVanguard401kPriceSharesAndCost(driver, account, book, planID)
                print('account balance is: ' + account.balance)
                change = round(Decimal(account.balance) - Decimal(account.gnuBalance),2)
                if change > 0:
                    writeAssetFundTransaction(book, account, change)
            account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
            account.setBalance(account.gnuBalance) 
    
if __name__ == '__main__':
    driver, book = Driver("Chrome"), GnuCash('Finance')
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    accounts = getVanguardAccounts(book)
    runVanguard401k(driver, accounts, book, gnuCashTransactions, lastMonth)
    book.closeBook()

# if __name__ == '__main__':
#     driver, book = Driver("Chrome"), GnuCash('Finance')
#     accounts = getVanguardAccounts(book)
#     runVanguardPension(driver, accounts, book)