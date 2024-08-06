import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Optum":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage, setDirectory, getPassword, getAnswerForSecurityQuestion)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage, setDirectory, getPassword, getAnswerForSecurityQuestion)  
    
def locateOptumWindow(driver):
    found = driver.findWindowByUrl("secure.optumfinancial.com")
    if not found:   optumLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    
# def answerOptumSecurityQuestions(driver):
#     try:
#         question = driver.webDriver.find_element(By.XPATH, "//*[@id='answer-0_container']/div[1]/label/span").text
#         print(question)
#         driver.webDriver.find_element(By.ID, 'answer-0').send_keys(getAnswerForSecurityQuestion(question))
#         driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/main/div[3]/div/div[2]/form/div/div[2]/div").click() # Trust this device
#         driver.webDriver.find_element(By.ID, 'submitBtn').click() # Continue
#     except NoSuchElementException:  exception = 'no security questions'
        
def optumLogin(driver):
    driver.openNewWindow('https://secure.optumfinancial.com/portal/hsid/login?url=/portal/CC')
    try:
        driver.webDriver.find_element(By.ID, "password").send_keys(getPassword('Optum HSA'))
        driver.webDriver.find_element(By.ID, "submitBtn").click() # Sign in
        time.sleep(3)
    #     answerOptumSecurityQuestions(driver)
    # except StaleElementReferenceException:
    #     answerOptumSecurityQuestions(driver)
    except NoSuchElementException:      exception = "already logged in"
    time.sleep(1)
    
def getOptumBalance(driver, accounts):
    locateOptumWindow(driver)
    optumPostLoginPageURL = "https://secure.optumfinancial.com/portal/CC/cdhportal"
    if not driver.webDriver.current_url == optumPostLoginPageURL:   driver.webDriver.get(optumPostLoginPageURL)
    accounts['OptumCash'].setBalance(driver.webDriver.find_element(By.ID,"availableToSpendBoxValue").text.replace("$","").replace(",",""))
    accounts['VFIAX'].setValue(driver.webDriver.find_element(By.ID,"investmentBalance").text.replace("$","").replace(",",""))

def getOptumPricesAndShares(driver, accounts, book):
    locateOptumWindow(driver)
    optumInvestPageURL = "https://secure.optumfinancial.com/portal/CC/cdhportal/cdhaccount/investcenter"
    if not driver.webDriver.current_url == optumInvestPageURL:  driver.webDriver.get(optumInvestPageURL)
    accounts['VFIAX'].price = driver.webDriver.find_element(By.XPATH,"//*[@id='investCenter']/div[4]/div/div[1]/div[2]/div/table/tbody/tr[1]/td[4]").text.replace("$","").replace(",","")
    book.updatePriceInGnucash(accounts['VFIAX'].symbol, accounts['VFIAX'].price)
    accounts['VFIAX'].setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='investCenter']/div[4]/div/div[1]/div[2]/div/table/tbody/tr[1]/td[3]").text.replace(",",""))
    
def setOptumTransactionPath(row, column):    return f"//*[@id='trans']/tbody/tr[{str(row)}]/td[{str(column)}]"

def captureOptumTransactions(driver, accounts):
    locateOptumWindow(driver)
    optumActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\optum.csv"
    open(optumActivity, 'w', newline='').truncate()
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    row = 0
    if "investcenter" not in driver.webDriver.current_url:
        driver.clickXPATHElementOnceAvaiable("//*[@id='investmentBox']/a") # Investments
    driver.clickXPATHElementOnceAvaiable("//*[@id='invest-center-submenu']/li[2]/a") # Investment Transactions
    driver.clickXPATHElementOnceAvaiable("//*[@id='investCenter']/div[3]/div[1]/div/div/a") # View all settled Transactions
    driver.webDriver.find_element(By.ID,"startDate").send_keys(lastMonth['startDate'].strftime('%m/%d/%Y'))
    driver.webDriver.find_element(By.ID,"endDate").send_keys(lastMonth['endDate'].strftime('%m/%d/%Y'))
    driver.webDriver.find_element(By.XPATH,"//*[@id='customDates']/div[4]/input").click() # Search
    while True:
        row+=1
        column = 1
        try:    dateElement = driver.webDriver.find_element(By.XPATH,setOptumTransactionPath(row, column))
        except NoSuchElementException:
            if row==1:  showMessage('Error finding Date Element', 'Element path for date element has changed, please update.')
            break
        date = datetime.strptime(dateElement.text, '%m/%d/%Y').date()
        if date.month == lastMonth['endDate'].month:
            column+=1
            description = driver.webDriver.find_element(By.XPATH,setOptumTransactionPath(row, column)).text
            column+=1
            description += " " + driver.webDriver.find_element(By.XPATH,setOptumTransactionPath(row, column)).text
            column+=1
            shares = driver.webDriver.find_element(By.XPATH,setOptumTransactionPath(row, column)).text
            column+=2
            amount = driver.webDriver.find_element(By.XPATH,setOptumTransactionPath(row, column)).text.replace('$','').replace(',','')
            transaction = date, description, shares, amount, accounts['VFIAX']
            csv.writer(open(optumActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month < lastMonth['endDate'].month or date.year < lastMonth['endDate'].year:  break
    return optumActivity

def runOptum(driver, accounts, book):
    locateOptumWindow(driver)
    getOptumBalance(driver, accounts)
    getOptumPricesAndShares(driver, accounts, book)
    optumActivity = captureOptumTransactions(driver, accounts)
    book.importGnuTransaction(accounts['VFIAX'], optumActivity, driver, 0)
    accounts['OptumCash'].updateGnuBalance(book.getBalance(accounts['OptumCash'].gnuAccount))
    accounts['VFIAX'].updateGnuBalanceAndValue(book.getBalance(accounts['VFIAX'].gnuAccount))
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    VFIAX = Security("VFIAX", book)
    OptumCash = USD("Optum Cash", book)
    OptumAccounts = {'VFIAX': VFIAX, 'OptumCash': OptumCash}
    runOptum(driver, OptumAccounts, book)
    book.closeBook()