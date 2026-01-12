import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "HealthEquity":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage, setDirectory, getUsername, getPassword)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage, setDirectory, getUsername, getPassword)

def locateHealthEquityWindow(driver):
    found = driver.findWindowByUrl("member.my.healthequity.com")
    if not found:   healthEquitylogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def closePopUps(driver):
    driver.getElementAndClick('xpath', "/html/body/div[2]/div[2]/div/mat-dialog-container/div/div/hqy-mobile-download-modal/div/button/mat-icon", wait=0.1) # X
    
def healthEquitylogin(driver):
    driver.openNewWindow('https://member.my.healthequity.com/hsa/21895515-010')
    driver.waitForWebPageLoad()
    userNameElement = driver.getElement('id', 'ctl00_modulePageContent_txtUserIdStandard', wait=2)
    if userNameElement:
        userNameElement.clear()
        driver.getElementAndSendKeys('id', 'ctl00_modulePageContent_txtUserIdStandard', getUsername('HealthEquity HSA'))
        driver.getElementAndClick('id', 'ctl00_modulePageContent_btnSubmitUsername') # Continue
        passwordElement = driver.getElement('id', 'ctl00_modulePageContent_txtPassword', wait=2)
        passwordElement.click()
        passwordElement.clear()
        driver.getElementAndSendKeys('id', 'ctl00_modulePageContent_txtPassword', getPassword('HealthEquity HSA'))
        driver.getElementAndClick('id', 'ctl00_modulePageContent_btnLogin') # login
        if driver.getElementAndClick('xpath', "//*[@id='sendEmailTextVoicePanel']/div[5]/span[1]/span/label/span/strong", wait=1): # send code to phone
            driver.getElementAndClick('id', 'sendOtp') # Send confirmation code
            showMessage("Confirmation Code", "Enter code then click OK") # enter text code
            driver.getElementAndClick('xpath', "//*[@id='VerifyOtpPanel']/div[4]/div[1]/div/label/span") # Remember me
            driver.getElementAndClick('id', 'verifyOtp') # click Confirm
        driver.getElementAndClick('xpath', "//*[@id='topmenu']/div[2]/a/span", wait=1) # Home button to bypass error
    closePopUps(driver)

def getHealthEquityBalances(driver, accounts):
    locateHealthEquityWindow(driver)
    time.sleep(2)
    cashBalance = driver.getElementText('xpath', "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/div/span[1]", allowFail=False)
    investValue = driver.getElementText('xpath', "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/span[2]/span[1]", allowFail=False)
    if not cashBalance and investValue:
        return False
    accounts['HECash'].setBalance(float(cashBalance.strip('$').replace(',','')))
    accounts['VIIIX'].value = float(investValue.strip('$').replace(',',''))
    driver.getElementAndClick('link_text', 'Manage investments')
    time.sleep(5)
    viiixBalance = driver.getElementText('id', 'desktopSharesHeld0', allowFail=False)
    if not viiixBalance:    return False
    accounts['VIIIX'].setBalance(viiixBalance)
    driver.getElementAndClick('xpath', "//*[@id='topmenu']/div[2]/a/span") # Home Button

def getHealthEquityCSVFile(account):
    accountName = account.name.replace(' ','').lower()
    return setDirectory() + f"/Projects/Coding/Python/FinanceAutomation/Resources/{accountName}.csv"

def clearHEDate(dates):
    for d in dates:
        num = 0
        while num < 10:
            d.click()
            d.send_keys(Keys.BACKSPACE)
            num += 1  

def captureHealthEquityInvestmentTransactionsBalanceAndCost(driver, account, book, lastMonth):
    locateHealthEquityWindow(driver)
    investmentActivity = getHealthEquityCSVFile(account)
    open(investmentActivity, 'w', newline='').truncate()
    time.sleep(5)
    driver.getElementAndClick('link_text', 'Manage investments')
    # time.sleep(3)
    driver.getElementAndClick('id', 'EditPortfolioTab') # Portfolio performance
    # time.sleep(4)
    driver.getElementAndClick('id', 'fundSelection') # Click Investment Fund Option
    num = 0
    startDateElement = driver.getElement('id', 'startDate')
    endDateElement = driver.getElement('id', 'endDate')
    clearHEDate([startDateElement, endDateElement])
    startDateElement.send_keys(datetime.strftime(datetime(2021,1,1,0,0).date(), '%m/%d/%Y'))
    endDateElement.send_keys(datetime.strftime(lastMonth['endDate'], '%m/%d/%Y'))
    driver.getElementAndClick('id', 'fundPerformanceRefresh') # Refresh
    costHeader = driver.getElementText('xpath', "//*[@id='EditPortfolioTab-panel']/member-portfolio-edit-display/member-overall-portfolio-performance-display/div[1]/div/div[2]", allowFail=False)
    if 'Trades' in costHeader:
        cost = driver.getElementText('xpath', "//*[@id='EditPortfolioTab-panel']/member-portfolio-edit-display/member-overall-portfolio-performance-display/div[1]/div/div[2]/div/span", allowFail=False)
        account.setCost(cost.replace('$', '').replace(',',''))
    num = 1        
    while True:
        element = driver.getElement('xpath', "//*[@id='fundSelection']/option[" + str(num) + "]")
        if element.text == account.symbol: element.click(); break
        else:   num+=1
    clearHEDate([startDateElement])  
    startDateElement.send_keys(datetime.strftime(lastMonth['startDate'], '%m/%d/%Y'))
    # endDateElement.send_keys(datetime.strftime(lastMonth['endDate'], '%m/%d/%Y'))
    driver.getElementAndClick('id', 'fundPerformanceRefresh') # Refresh
    # time.sleep(1)
    row = 1 # Skip 0 which should be "Starting Balance"
    while True:
        description = driver.getElementText('id', "desktopDescription" + str(row), allowFail=False)
        if 'Buy' in description or 'Dividend' in description:
            date = datetime.strptime(driver.getElementText('id', "desktopDate" + str(row), allowFail=False), '%m/%d/%Y').date()
            amount = driver.getElementText('id', "desktopAmount" + str(row), allowFail=False).strip('$')
            shares = driver.getElementText('id', "desktopSharesPurchased" + str(row), allowFail=False)
            transaction = date, description, amount, shares
            csv.writer(open(investmentActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
            row+=1
        elif 'Ending Balance' in description:
            account.price = Decimal(driver.getElementText('id', "desktopPrice" + str(row), allowFail=False).replace('$', ''))
            book.updatePriceInGnucash(account.symbol, account.price)
            account.setBalance(driver.getElementText('xpath', "//*[@id='desktopTotalShares" + str(row) + "']/span", allowFail=False))
            account.value = driver.getElementText('xpath', "//*[@id='desktopTotalValue" + str(row) + "']/span", allowFail=False).replace('$', '').replace(',','')
            break
        else:   showMessage('Unknown Transaction: ' + description, "check Investment transaction list for undefined transaction")
    return investmentActivity

def captureHealthEquityCashTransactionsAndBalance(driver, account, lastMonth):
    locateHealthEquityWindow(driver)
    driver.webDriver.get('https://my.healthequity.com/Member/MemberTransactions.aspx?Subaccount=HSA')
    cashActivity = getHealthEquityCSVFile(account)
    open(cashActivity, 'w', newline='').truncate()
    driver.getElementAndClick('xpath', "/html/body/form/div[3]/div/div/div[1]/div/div[2]/span/div[2]/section/section[2]/div/div[2]/select") # Date range drop-down
    driver.getElementAndClick('xpath', "/html/body/form/div[3]/div/div/div[1]/div/div[2]/span/div[2]/section/section[2]/div/div[2]/select/option[1]") # All dates
    time.sleep(1)
    row = 1
    while True:
        column=1
        row+=1
        dateString = driver.getElementText('xpath', "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]")
        postDate = datetime.strptime(dateString, '%m/%d/%Y').date()
        if postDate.month == lastMonth['endDate'].month:
            column+=1
            description = driver.getElementText('xpath', "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]")
            if 'Investment Admin Fee' in description or 'Interest' in description or 'Employer Contribution' in description:
                column+=1
                amount = driver.getElementText('xpath', "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").replace('(','').replace('$','').replace(')','')
                amount = -Decimal(amount) if 'Fee' in description else amount
                transaction = postDate, description, amount
                csv.writer(open(cashActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                if "Interest" in description:
                    column+=1
                    account.setBalance(driver.getElementText('xpath', "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/span").replace('$','').replace(',',''))
            elif 'Employee Contribution' in description or 'Investment: ' in description:   continue
            else:   showMessage('Unknown Transaction: ' + description, "check Cash transaction list for undefined transaction"); break
        elif postDate.month < lastMonth['endDate'].month or postDate.year < lastMonth['endDate'].year: break
    return cashActivity

def getHealthEquityAccounts(book):
    return {'HECash': USD("HE Cash", book), 'VIIIX': Security("VIIIX", book)}

def importHealthEquityTransactions(account, HEActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(HEActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1]
        description = rawDescription        
        amount = Decimal(row[2])
        shares = 0
        try:                shares = float(row[3])
        except IndexError:  exception = 'no shares found in transaction'
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "VIIIX: Buy" in rawDescription:
            description = "HSA VIIIX Investment"
            toAccount = book.getGnuAccountFullName('HE Cash')
        elif "VBIRX: Buy" in rawDescription:                                        
            description = "HSA VBIRX Investment"
            toAccount = book.getGnuAccountFullName('HE Cash')
        elif "Dividend" in rawDescription:                                          
            description = "HSA Dividend"
            toAccount = book.getGnuAccountFullName('Dividends')
        elif "Employer Contribution" in rawDescription:                             
            description = 'HSA Employer Contribution'
            toAccount = book.getGnuAccountFullName('HSA Contributions')
        elif "Interest" in rawDescription:                                          
            description = 'Interest Earned'
            toAccount = book.getGnuAccountFullName('Interest')
        elif 'Investment Admin Fee ' in rawDescription:                              
            description = 'HSA Fee'
            toAccount = book.getGnuAccountFullName('Bank Fees')
        # toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        if shares:      splits = [{'amount': -amount, 'account':toAccount},{'amount': amount, 'account':fromAccount, 'quantity': round(Decimal(shares),3)}]
        else:           splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

def runHealthEquity(driver, accounts, book, gnuCashTransactions, lastMonth):
    locateHealthEquityWindow(driver)
    getHealthEquityBalances(driver, accounts)
    for accountName in list(accounts.keys()):
        account = accounts.get(accountName)
        if accountName == 'VIIIX' or accountName == 'VBIRX':
            HEactivity = captureHealthEquityInvestmentTransactionsBalanceAndCost(driver, account, book, lastMonth)
        elif accountName == 'HECash':
            HEactivity = captureHealthEquityCashTransactionsAndBalance(driver, account, lastMonth)
        importHealthEquityTransactions(account, HEactivity, book, gnuCashTransactions)
        balance = book.getGnuAccountBalance(account.gnuAccount)
        if hasattr(account, 'symbol'):  account.updateGnuBalanceAndValue(balance)
        else:                           account.updateGnuBalance(balance)

# if __name__ == '__main__':
#     driver, book = Driver("Chrome"), GnuCash('Finance')
#     HEaccounts = getHealthEquityAccounts(book)
#     lastMonth = getStartAndEndOfDateRange(timeSpan="month")
#     gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
#     runHealthEquity(driver, HEaccounts, book, gnuCashTransactions, lastMonth)
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateHealthEquityWindow(driver)
