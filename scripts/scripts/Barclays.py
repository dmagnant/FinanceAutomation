import os, time, csv
from datetime import datetime
from decimal import Decimal
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Barclays":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, showMessage, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, showMessage, getStartAndEndOfDateRange)

def locateBarclaysWindow(driver):
    found = driver.findWindowByUrl("barclaycardus.com")
    if not found:
        barclaysLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)     

def barclaysLogin(driver):
    driver.openNewWindow('https://www.barclaycardus.com/servicing/home?secureLogin=')
    driver = driver.webDriver 
    # Login
    try:
        driver.find_element(By.ID, "username").send_keys(getUsername('Barclay Card'))
    except ElementNotInteractableException: exception = 'username already entered'
    try:
        driver.find_element(By.ID, "password").send_keys(getPassword('Barclay Card'))
    except ElementNotInteractableException: exception = 'password already entered'
    driver.find_element(By.ID, "loginButton").click()
    # handle security questions
    try:
        question1 = driver.find_element(By.ID, "question1TxtbxLabel").text
        question2 = driver.find_element(By.ID, "question2TxtbxLabel").text
        q1 = "In what year was your mother born?"
        a1 = os.environ.get('MotherBirthYear')
        q2 = "What is the name of the first company you worked for?"
        a2 = os.environ.get('FirstEmployer')
        if question1 == q1:
            driver.find_element(By.ID, "rsaAns1").send_keys(a1)
            driver.find_element(By.ID, "rsaAns2").send_keys(a2)
        else:
            driver.find_element(By.ID, "rsaAns1").send_keys(a2)
            driver.find_element(By.ID, "rsaAns2").send_keys(a1)
        driver.find_element(By.ID, "rsaChallengeFormSubmitButton").click()
    except NoSuchElementException:  exception = "Caught"
    # handle Confirm Your Identity
    try:
        driver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div/div/div[2]/div[1]/label/span").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        # User pop-up to enter SecurPass Code
        showMessage("Get Code From Phone", "Enter in box, then click OK")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
    except NoSuchElementException:  exception = "Caught"
    try:    driver.find_element(By.XPATH, "/html/body/div[4]/div/button/span").click() # close pop-up
    except NoSuchElementException:  exception = "Caught"

def getBarclaysBalance(driver):
    locateBarclaysWindow(driver)     
    return driver.webDriver.find_element(By.XPATH, "//*[@id='accountTile']/div[2]/div/div[2]/div[1]/div").text.strip('-').strip('$').replace(',', '')

def exportBarclaysTransactions(driver, today):
    # # EXPORT TRANSACTIONS
    # click on Activity & Statements
    driver.find_element(By.XPATH, "/html/body/section[2]/div[1]/nav/div/ul/li[3]/a").click()
    # Click on Transactions
    driver.find_element(By.XPATH, "/html/body/section[2]/div[1]/nav/div/ul/li[3]/ul/li/div/div[2]/ul/li[1]/a").click()
    driver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div/div/div[3]/div[1]/div/div[2]/span/div/button/span[1]").click() # download
    year, month = today.year, today.month
    monthTo, yrTO, yearTo = str(month), str(year - 2000), str(year)
    if month == 1:  monthFrom, yrFROM, yearFrom = "12", str(year - 2001), str(year - 1)
    else:           monthFrom, yrFROM, yearFrom = str(month - 1), yrTO, yearTo
    # enter date_range
    driver.find_element(By.ID, "downloadFromDate_input").send_keys(monthFrom + "/05/" + yrFROM)
    driver.find_element(By.ID, "downloadToDate_input").send_keys(monthTo + "/04/" + yrTO)
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/div[2]/div/form/div[3]/div/button").click() # Download
    time.sleep(2)
    return r"C:\Users\dmagn\Downloads\CreditCard_" + yearFrom + monthFrom + "05_" + yearTo + monthTo + "04.csv"

def claimBarclaysRewards(driver):
    locateBarclaysWindow(driver)
    driver = driver.webDriver
    driver.get("https://www.barclaycardus.com/servicing/cashBack?__fsk=337615032#!/redeem")
    driver.find_element(By.ID,"redeem-continue").click() # continue
    driver.find_element(By.ID, "mor_dropDown0").click() # reward method
    driver.find_element(By.ID, "mor_dropDown0").send_keys(Keys.DOWN)
    driver.find_element(By.ID, "mor_dropDown0").send_keys(Keys.ENTER)
    time.sleep(1)
    driver.find_element(By.ID, "achModal-continue").click()
    time.sleep(1)
    driver.find_element(By.ID, "redeem-continue").click() # redeem now

def importBarclaysTransactions(account, barclaysActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(barclaysActivity), delimiter=','):
        reviewTransaction = False
        if num <5: num+=1; continue # skip header lines
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[1]
        amount = Decimal(row[3])
        fromAccount = account.gnuAccount
        if "PAYMENT RECEIVED" in rawDescription.upper():   continue
        elif "BARCLAYCARD US" in rawDescription.upper() and float(amount) > 0:         description = "Barclays CC Rewards"
        else:                                                                       description = rawDescription
        toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)
        account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))


def runBarclays(driver, account, book):
    today = datetime.today()
    locateBarclaysWindow(driver)
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    account.setBalance(getBarclaysBalance(driver))
    rewardsBalance = float(driver.webDriver.find_element(By.XPATH, "//*[@id='rewardsTile']/div[2]/div/div[2]/div[1]/div").text.strip('$'))
    barclaysActivity = exportBarclaysTransactions(driver.webDriver, today)
    if rewardsBalance >= float(50): claimBarclaysRewards(driver)
    importBarclaysTransactions(account, barclaysActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

if __name__ == '__main__':
    # driver = Driver("Chrome")
    # book = GnuCash('Finance')
    # Barclays = USD("Barclays", book)    
    # runBarclays(driver, Barclays, book)
    # Barclays.getData()
    # book.closeBook()
    
    
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Barclays = USD("Barclays", book)   
    Barclays.setBalance(float(116.22))
    Barclays.locateAndUpdateSpreadsheet(driver)
