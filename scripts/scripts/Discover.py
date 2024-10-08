import time, csv
from decimal import Decimal
from datetime import datetime

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Discover":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash    
    from Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange

def locateDiscoverWindow(driver):
    found = driver.findWindowByUrl("discover.com")
    if not found:   discoverLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def discoverLogin(driver):
    driver.openNewWindow('https://portal.discover.com/customersvcs/universalLogin/ac_main') 
    # login
    # username already entered
    # driver.find_element(By.ID, 'userid-content').send_keys(getUsername('Discover'))
    # driver.webDriver.find_element(By.ID, 'password-content').send_keys(getPassword('Discover'))
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[1]/div/form/input[8]').click()

    #handle pop-up
    try:    driver.find_element(By.XPATH, "//*[@id='root']/div[4]/div/div/button/img").click()
    except (NoSuchElementException, ElementNotInteractableException, AttributeError): exception = "caught"

def getDiscoverBalance(driver):
    locateDiscoverWindow(driver)
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/statements/app/activity#/current")
    time.sleep(1)
    return driver.webDriver.find_element(By.ID, "new-balance").text.strip('$')

def exportDiscoverTransactions(driver, today):
    driver.find_element(By.XPATH, "//*[@id='current-statement']/div[1]/div/a[2]").click() # download
    driver.find_element(By.ID, "radio4").click() # csv
    driver.find_element(By.ID, "submitDownload").click() # download
    driver.find_element(By.XPATH, "//*[@id='downloadForm']/div/div[4]/a[1]/i").click() # x to close
    stmtYear, stmtMonth = str(today.year), today.strftime('%m')
    return r"C:\Users\dmagn\Downloads\Discover-Statement-" + stmtYear + stmtMonth + "12.csv"

def claimDiscoverRewards(driver, account):
    locateDiscoverWindow(driver)    
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/rewards/app/redemption?ICMPGN=AC_NAV_L3_REDEEM#/cash")
    balance = driver.webDriver.find_element(By.XPATH,"//*[@id='main-content-rwd']/div/div/div[1]/section[2]/div/div/span").text.replace(' Available', '').replace('$','')
    if float(balance) > 0:
        driver.webDriver.find_element(By.ID, "electronic-deposit").click() # Electronic Deposit to your bank account
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/form/div[2]/fieldset/div[3]/div[2]/span[2]/button").click() # Redeem All link
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH, "//*[@id='cashbackForm']/div[4]/input").click() # Continue
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/div/div/div[1]/div/div/div[2]/div/button[1]").click() # Submit
    account.setValue(float(balance))
    if account.value:   account.value = account.balance - account.value
    print('balance: ' + account.balance)
    print('value: ' + account.value)

def importDiscoverTransactions(account, discoverActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(discoverActivity), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[1], '%m/%d/%Y').date()
        rawDescription = row[2]
        amount = -Decimal(row[3])
        fromAccount = account.gnuAccount
        if "DIRECTPAY FULL BALANCE" in rawDescription.upper():                  continue
        elif "AUTOMATIC STATEMENT CREDIT" in description.upper():               description = "Discover CC Rewards"        
        else:                                                                   description = rawDescription
        toAccount = book.getGnuAccountName(fromAccount, description=description, row=row)
        if toAccount == 'Expenses:Other': reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runDiscover(driver, account, book):
    today = datetime.today()
    locateDiscoverWindow(driver)
    account.setBalance(getDiscoverBalance(driver))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    discoverActivity = exportDiscoverTransactions(driver.webDriver, today)
    claimDiscoverRewards(driver, account)
    importDiscoverTransactions(account, discoverActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    # book.importGnuTransaction(account, discoverActivity, driver)
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions: book.openGnuCashUI()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Discover = USD("Discover", book)
    runDiscover(driver, Discover, book)
    Discover.getData()
    book.closeBook()

    