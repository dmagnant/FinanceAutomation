import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "HealthEquity":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage, setDirectory)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage, setDirectory)    

def locateHealthEquityWindow(driver):
    found = driver.findWindowByUrl("member.my.healthequity.com")
    if not found:   healthEquitylogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def healthEquitylogin(driver):
    driver.openNewWindow('https://member.my.healthequity.com/hsa/21895515-010')
    try:
        driver.clickIDElementOnceAvailable("ctl00_modulePageContent_txtUserIdStandard")
        driver.webDriver.find_element(By.ID,"ctl00_modulePageContent_txtPassword").click()
        driver.webDriver.find_element(By.ID, "ctl00_modulePageContent_btnLogin").click() # login
        try:  # Two-Step Authentication
            driver.webDriver.find_element(By.XPATH, "//*[@id='sendEmailTextVoicePanel']/div[5]/span[1]/span/label/span/strong").click() # send code to phone
            driver.webDriver.find_element(By.ID, "sendOtp").click() # Send confirmation code
            showMessage("Confirmation Code", "Enter code then click OK") # enter text code
            driver.webDriver.find_element(By.XPATH, "//*[@id='VerifyOtpPanel']/div[4]/div[1]/div/label/span").click() # Remember me
            driver.webDriver.find_element(By.ID, "verifyOtp").click() # click Confirm
        except NoSuchElementException:  exception = "already verified"
        try:    driver.webDriver.find_element(By.XPATH,"//*[@id='topmenu']/div[2]/a/span").click() # Home button to bypass error
        except NoSuchElementException:  exception = "no error to bypass"
    except NoSuchElementException:      exception = "already logged in"
    time.sleep(1)

def getHealthEquityBalances(driver, accounts):
    locateHealthEquityWindow(driver)
    time.sleep(2)
    cashBalance = float(driver.webDriver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/div/span[1]").text.strip('$').replace(',',''))
    accounts['HECash'].setBalance(cashBalance)
    investValue = float(driver.webDriver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/span[2]/span[1]").text.strip('$').replace(',',''))
    accounts['VIIIX'].value = investValue
    driver.webDriver.find_element(By.LINK_TEXT, "Manage investments").click()
    time.sleep(5)
    accounts['VIIIX'].setBalance(driver.webDriver.find_element(By.ID,'desktopSharesHeld0').text)
    driver.webDriver.find_element(By.XPATH,"//*[@id='topmenu']/div[2]/a/span").click() # Home Button

def getHealthEquityCSVFile(account):
    accountName = account.name.replace(' ','').lower()
    return setDirectory() + f"\Projects\Coding\Python\FinanceAutomation\Resources\{accountName}.csv"

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
    driver.webDriver.find_element(By.LINK_TEXT, "Manage investments").click()
    time.sleep(3)
    driver.webDriver.find_element(By.ID, "EditPortfolioTab").click() # Portfolio performance
    time.sleep(4)
    driver.webDriver.find_element(By.ID, "fundSelection").click() # Click Investment Fund Option
    num = 0
    startDateElement = driver.webDriver.find_element(By.ID, "startDate")
    endDateElement = driver.webDriver.find_element(By.ID, "endDate")
    clearHEDate([startDateElement, endDateElement])  
    startDateElement.send_keys(datetime.strftime(datetime(2021,1,1,0,0).date(), '%m/%d/%Y'))
    endDateElement.send_keys(datetime.strftime(lastMonth['endDate'], '%m/%d/%Y'))
    driver.webDriver.find_element(By.ID, "fundPerformanceRefresh").click() # Refresh
    costHeader = driver.webDriver.find_element(By.XPATH, "//*[@id='EditPortfolioTab-panel']/member-portfolio-edit-display/member-overall-portfolio-performance-display/div[1]/div/div[2]").text
    if 'Trades' in costHeader:
        cost = driver.webDriver.find_element(By.XPATH, "//*[@id='EditPortfolioTab-panel']/member-portfolio-edit-display/member-overall-portfolio-performance-display/div[1]/div/div[2]/div/span").text.replace('$', '').replace(',','')
        print(cost)
        account.setCost(cost)
    num = 1        
    while True:
        element = driver.webDriver.find_element(By.XPATH, "//*[@id='fundSelection']/option[" + str(num) + "]")
        if element.text == account.symbol: element.click(); break
        else:   num+=1
    clearHEDate([startDateElement])  
    startDateElement.send_keys(datetime.strftime(lastMonth['startDate'], '%m/%d/%Y'))
    # endDateElement.send_keys(datetime.strftime(lastMonth['endDate'], '%m/%d/%Y'))
    driver.webDriver.find_element(By.ID, "fundPerformanceRefresh").click() # Refresh
    time.sleep(1)
    row = 1 # Skip 0 which should be "Starting Balance"
    while True:
        description = driver.webDriver.find_element(By.ID, "desktopDescription" + str(row)).text
        if 'Buy' in description or 'Dividend' in description:
            date = datetime.strptime(driver.webDriver.find_element(By.ID, "desktopDate" + str(row)).text, '%m/%d/%Y').date()
            amount = driver.webDriver.find_element(By.ID, "desktopAmount" + str(row)).text.strip('$')
            shares = driver.webDriver.find_element(By.ID, "desktopSharesPurchased" + str(row)).text
            transaction = date, description, amount, shares
            csv.writer(open(investmentActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
            row+=1
        elif 'Ending Balance' in description:
            account.price = Decimal(driver.webDriver.find_element(By.ID, "desktopPrice" + str(row)).text.replace('$', ''))
            book.updatePriceInGnucash(account.symbol, account.price)
            account.setBalance(driver.webDriver.find_element(By.XPATH, "//*[@id='desktopTotalShares" + str(row) + "']/span").text)
            account.value = driver.webDriver.find_element(By.XPATH, "//*[@id='desktopTotalValue" + str(row) + "']/span").text.replace('$', '').replace(',','')
            break
        else:   showMessage('Unknown Transaction: ' + description, "check Investment transaction list for undefined transaction")

    return investmentActivity

def captureHealthEquityCashTransactionsAndBalance(driver, account, lastMonth):
    locateHealthEquityWindow(driver)
    driver.webDriver.get('https://my.healthequity.com/Member/MemberTransactions.aspx?Subaccount=HSA')
    cashActivity = getHealthEquityCSVFile(account)
    open(cashActivity, 'w', newline='').truncate()
    driver.webDriver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/div[1]/div/div[2]/span/div[2]/section/section[2]/div/div[2]/select").click() # Date range drop-down
    driver.webDriver.find_element(By.XPATH, "/html/body/form/div[3]/div/div/div[1]/div/div[2]/span/div[2]/section/section[2]/div/div[2]/select/option[1]").click() # All dates
    time.sleep(1)
    row = 1
    while True:
        column=1
        row+=1
        dateString = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text
        postDate = datetime.strptime(dateString, '%m/%d/%Y').date()
        if postDate.month == lastMonth['endDate'].month:
            column+=1
            description = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text
            if 'Investment Admin Fee' in description or 'Interest' in description or 'Employer Contribution' in description:
                column+=1
                amount = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text.replace('(','').replace('$','').replace(')','')
                amount = -Decimal(amount) if 'Fee' in description else amount
                transaction = postDate, description, amount
                csv.writer(open(cashActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                if "Interest" in description:
                    column+=1
                    account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/span").text.replace('$','').replace(',',''))
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
    driver, book = Driver("Chrome"), GnuCash('Finance')
    HEaccounts = getHealthEquityAccounts(book)
    HEaccounts['VIIIX'].getData()