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
    found = driver.findWindowByUrl("comenity.net")
    if not found:   gamestopCCLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1) 
        
def gamestopCCLogin(driver):
    driver.openNewWindow('https://d.comenity.net/ac/gamestop/public/home')
    driver.clickIDElementOnceAvailable("existing-cardmember-sign-in-button-link")
    # driver.getIDElementOnceAvailable("username-data-field").send_keys(getUsername('Comenity'))
    driver.getIDElementOnceAvailable("password-data-field").send_keys(getPassword('Comenity'))
    driver.clickIDElementOnceAvailable("sign-in-button-link")
    time.sleep(1)

def getGamestopCCBalance(driver):
    locateGamestopCCWindow(driver)
    for element in driver.webDriver.find_elements(By.XPATH,"//p[@class='" + 'due' + "']"):
        if "Statement Balance" in element.text:
            return element.text.replace('Statement Balance: $', '')

def exportGamestopCCTransactions(driver):
    locateGamestopCCWindow(driver)
    driver.clickIDElementOnceAvailable("account-activity-header")

def importGamestopCCTransactions(account, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(r'C:\Users\dmagn\Downloads\TITLE FOR GME CC STATEMENT FILE.csv'), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[1]
        amount = -Decimal(row[2])
        fromAccount = account.gnuAccount
        if "AUTOPAY PAYMENT" in rawDescription.upper():                             continue
        elif "YOUR CASH REWARD/REFUND IS" in rawDescription.upper():                description = "Gamestop CC Rewards"
        else:                                                                       description = rawDescription
        toAccount = book.getGnuAccountFullName(fromAccount, description=description, row=row)
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runGamestopCC(driver, account, book):
    locateGamestopCCWindow(driver)
    account.setBalance(getGamestopCCBalance(driver))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    exportGamestopCCTransactions(driver.webDriver)
    importGamestopCCTransactions(account, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     GamestopCC = USD("GamestopCC", book)
#     runGamestopCC(driver, GamestopCC, book)
#     GamestopCC.getData()
#     book.closeBook()

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     GamestopCC = USD("Gamestop CC", book)
#     GamestopCC.setBalance(getGamestopCCBalance(driver))
#     # claimGamestopCCRewards(driver, GamestopCC)
#     book.closeBook()

if __name__ == '__main__':
    book = GnuCash('Finance')
    # CC = USD("Credit Cards", book)
    GamestopCC = USD("Gamestop CC", book)
    gnuAccount = book.getGnuAccountByFullName('Liabilities:Credit Cards')
    accounts = {}
    for child in gnuAccount.children:
        print(child.name)
        accounts[child.name] = USD(child.name, book)

    print(accounts)
    # account = book.accounts(fullname='Test') # Key error
    # print(account)
    # for spl in account.splits:
    #     print(spl)

    book.closeBook()

