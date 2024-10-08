import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "GamestopCC":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)

def getGamestopCCBasePath():  return '/html/body/div[1]/div[2]/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div'
            
def locateGamestopCCWindow(driver):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:   gamestopCCLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1) 
        
def gamestopCCLogin(driver):
    driver.openNewWindow('https://www.americanexpress.com/en-us/account/login?inav=iNavLnkLog')
    # driver.webDriver.find_element(By.ID, "eliloUserID").send_keys(getUsername('GamestopCC'))
    # driver.webDriver.find_element(By.ID, "eliloPassword").send_keys(getPassword('GamestopCC'))
    driver.webDriver.find_element(By.ID, "loginSubmit").click()
    try: driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span").click() # close pop-up
    except NoSuchElementException:  exception = "caught"
    time.sleep(1)

def getGamestopCCBalance(driver):
    locateGamestopCCWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[1]/div[1]/div/div[1]/div/div/span[1]/div").text.replace('$', '')

def exportGamestopCCTransactions(driver):
    driver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[2]/div[2]/div/div[1]/div[1]/div/a").click() # view transactions
    try: driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span").click() # view activity
    except NoSuchElementException:exception = "caught"
    time.sleep(6) 
    driver.find_element(By.XPATH, getGamestopCCBasePath() + "/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/button/div/p").click() # download arrow
    driver.find_element(By.XPATH, getGamestopCCBasePath() + "[1]/div/div/div/div/div/div[2]/div/div/div[1]/div/fieldset/div[2]/label").click() # CSV Option    
    try: os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:   exception = "caught"
    driver.find_element(By.XPATH, getGamestopCCBasePath() + "[1]/div/div/div/div/div/div[3]/div/a/span").click() # Download
    time.sleep(3)

def claimGamestopCCRewards(driver, account):
    locateGamestopCCWindow(driver)   
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    rewardsBalance = driver.webDriver.find_element(By.ID, "globalmrnavpointbalance").text.replace('$', '')
    if float(rewardsBalance) > 0:
        driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(rewardsBalance)
        driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(Keys.TAB)
        driver.webDriver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
        driver.webDriver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()
    account.setValue(float(rewardsBalance))
    if account.value:
        account.value = account.balance - account.value
    print('balance: ' + account.balance)
    print('value: ' + account.value)

def importGamestopCCTransactions(account, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(r'C:\Users\dmagn\Downloads\activity.csv'), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[1]
        amount = -Decimal(row[2])
        fromAccount = account.gnuAccount
        if "AUTOPAY PAYMENT" in rawDescription.upper():                             continue
        elif "YOUR CASH REWARD/REFUND IS" in rawDescription.upper():                description = "GamestopCC CC Rewards"
        else:                                                                       description = rawDescription
        toAccount = book.getGnuAccountName(fromAccount, description=description, row=row)
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runGamestopCC(driver, account, book):
    locateGamestopCCWindow(driver)
    account.setBalance(getGamestopCCBalance(driver))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    exportGamestopCCTransactions(driver.webDriver)
    claimGamestopCCRewards(driver, account)
    importGamestopCCTransactions(account, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    # book.importGnuTransaction(account, r'C:\Users\dmagn\Downloads\activity.csv', driver)
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     GamestopCC = USD("GamestopCC", book)
#     runGamestopCC(driver, GamestopCC, book)
#     GamestopCC.getData()
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    GamestopCC = USD("GamestopCC", book)
    GamestopCC.setBalance(getGamestopCCBalance(driver))
    claimGamestopCCRewards(driver, GamestopCC)
