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
    if not found:
        healthEquitylogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def healthEquitylogin(driver):
    driver.openNewWindow('https://member.my.healthequity.com/hsa/21895515-010')
    driver = driver.webDriver
    try:
        driver.find_element(By.ID, "ctl00_modulePageContent_btnLogin").click() # login
        try:  # Two-Step Authentication
            driver.find_element(By.XPATH, "//*[@id='sendEmailTextVoicePanel']/div[5]/span[1]/span/label/span/strong").click() # send code to phone
            driver.find_element(By.ID, "sendOtp").click() # Send confirmation code
            showMessage("Confirmation Code", "Enter code then click OK") # enter text code
            driver.find_element(By.XPATH, "//*[@id='VerifyOtpPanel']/div[4]/div[1]/div/label/span").click() # Remember me
            driver.find_element(By.ID, "verifyOtp").click() # click Confirm
        except NoSuchElementException:
            exception = "already verified"
    except NoSuchElementException:
        exception = "already logged in"
    time.sleep(1)

def getHealthEquityBalances(driver, accounts):
    locateHealthEquityWindow(driver)
    cashBalance = float(driver.webDriver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/div/span[1]").text.strip('$').replace(',',''))
    accounts['HECash'].setBalance(cashBalance)
    investValue = float(driver.webDriver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/span[2]/span[1]").text.strip('$').replace(',',''))
    accounts['HEInvestment'].value = investValue
    vanguard401kbalance = float(driver.webDriver.find_element(By.XPATH, "//*[@id='retirementAccounts']/li/a/div/ul/li/span[2]").text.strip('$').replace(',',''))
    accounts['V401k'].setBalance(vanguard401kbalance)
    driver.webDriver.find_element(By.XPATH, "//*[@id='hsaInvestment']/div/div/a").click() # Manage HSA Investments
    time.sleep(5)
    accounts['HEInvestment'].setBalance(driver.webDriver.find_element(By.ID,'desktopSharesHeld0').text)
    driver.webDriver.find_element(By.XPATH,"//*[@id='topmenu']/div[2]/a/span").click() # Home Button

def captureHealthEquityInvestmentTransactions(driver, accounts):
    locateHealthEquityWindow(driver)
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    investmentActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\hsainvestment.csv"
    open(investmentActivity, 'w', newline='').truncate()
    time.sleep(5)
    driver.webDriver.find_element(By.XPATH, "//*[@id='hsaInvestment']/div/div/a").click() # Manage HSA Investments
    time.sleep(2)
    driver.webDriver.find_element(By.ID, "EditPortfolioTab").click() # Portfolio performance
    time.sleep(4)
    driver.webDriver.find_element(By.ID, "fundSelection").click() # Click Investment Fund Option
    num = 1
    while True:
        element = driver.webDriver.find_element(By.XPATH, "//*[@id='fundSelection']/option[" + str(num) + "]")
        if element.text == 'VIIIX':
            element.click()
            break
        else:
            num+=1
    num = 0
    startDateElement = driver.webDriver.find_element(By.ID, "startDate")
    endDateElement = driver.webDriver.find_element(By.ID, "endDate")
    while num < 10:     # enter Start Date and End Date
        startDateElement.click()
        startDateElement.send_keys(Keys.BACKSPACE)
        endDateElement.click()
        endDateElement.send_keys(Keys.BACKSPACE)  
        num += 1
    startDateElement.send_keys(datetime.strftime(lastMonth['startDate'], '%m/%d/%Y'))
    endDateElement.send_keys(datetime.strftime(lastMonth['endDate'], '%m/%d/%Y'))
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
            accounts['HEInvestment'].units = driver.webDriver.find_element(By.XPATH, "//*[@id='desktopTotalShares" + str(row) + "']/span").text
            break
        else:
            showMessage('Unknown Transaction: ' + description, "check Investment transaction list for undefined transaction")
    return investmentActivity

def captureHealthEquityCashTransactions(driver):
    locateHealthEquityWindow(driver)
    driver.webDriver.get('https://my.healthequity.com/Member/MemberTransactions.aspx?Subaccount=HSA')
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    cashActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\hsacash.csv"
    open(cashActivity, 'w', newline='').truncate()
    row = 1
    while True:
        column=1
        row+=1
        dateString = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text
        postDate = datetime.strptime(dateString, '%m/%d/%Y').date()
        if postDate.month == lastMonth['endDate'].month:
            column+=1
            description = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text
            if 'Investment Admin Fee' in description or 'Interest' in description:
                column+=1
                amount = driver.webDriver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines']/tbody/tr[" + str(row) + "]/td[" + str(column) + "]").text.replace('(','').replace('$','').replace(')','')
                transaction = postDate, description, amount
                csv.writer(open(cashActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif postDate.month > lastMonth['endDate'].month:
            continue
        else:
            break
    return cashActivity
    
def runHealthEquity(driver, accounts, book):
    locateHealthEquityWindow(driver)
    getHealthEquityBalances(driver, accounts)
    investmentActivity = captureHealthEquityInvestmentTransactions(driver, accounts)
    book.importGnuTransaction(accounts['HEInvestment'], investmentActivity, driver, 0)
    cashActivity = captureHealthEquityCashTransactions(driver)
    book.importGnuTransaction(accounts['HECash'], cashActivity, driver, 0)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    HEInvestment = Security("HSA Investment", book)
    HECash = USD("HSA Cash", book)
    V401k = USD("Vanguard401k", book)
    HEaccounts = {'HEInvestment': HEInvestment, 'HECash': HECash, 'V401k': V401k}
    runHealthEquity(driver, HEaccounts, book)
    book.closeBook()
