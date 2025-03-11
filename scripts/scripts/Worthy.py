import time
from decimal import Decimal
from datetime import datetime

if __name__ == '__main__' or __name__ == "Worthy":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)

def locateWorthyWindow(driver):
    found = driver.findWindowByUrl("worthy.capital")
    if not found:
        worthyLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)

def worthyLogin(driver):
    driver.openNewWindow('https://worthy.capital/auth/login/')
    time.sleep(1)
    # driver.getElementAndSendKeys('id', 'email', getUsername('Worthy'), wait=2)
    # driver.getElementAndSendKeys('id', 'password', getPassword('Worthy'), wait=2)
    driver.getElementAndClick('id', 'password') # to activate page
    driver.getElementAndClick('xpath', "//*[@id='__next']/div/div/main/div/form/div[3]/button") # sign in
    # time.sleep(3)

def getWorthyBalance(driver, account):
    locateWorthyWindow(driver)
    # time.sleep(1)
    rawBalance = driver.getElementText('xpath', "//*[@id='__next']/div/div/main/div/div/div[1]/div/div/p/strong", allowFail=False)
    if rawBalance:
        account.setBalance(float(Decimal(rawBalance.strip('$').replace(',','').replace('*', ''))))

def importWorthyTransactions(account, book, date, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    description = "Interest Earned"
    change = round(Decimal(account.balance - float(account.gnuBalance)), 2)
    if change > 0:
        splits = [{'amount': change,'account': account.gnuAccount}, {'amount': -change,'account': "Income:Investments:Interest"}]
        book.writeUniqueTransaction(account, existingTransactions, date, description, splits)
        account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))

def runWorthy(driver, account, book, gnuCashTransactions, date):
    locateWorthyWindow(driver)
    getWorthyBalance(driver, account)
    importWorthyTransactions(account, book, date, gnuCashTransactions)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')    
    Worthy = USD("Worthy", book)
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    runWorthy(driver, Worthy, book, lastMonth['endDate'], gnuCashTransactions)
    Worthy.getData()
    book.closeBook()
    