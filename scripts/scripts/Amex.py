import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)

def closeAmexPopUps(driver):
    elementPath = '/html/body/div[1]/div/main/section/div[3]/div/div/div[1]/div/div/div/div/div/div/div/header/button/div/span[2]/svg'
    driver.getElementAndClick('xpath', elementPath, allowFail=True, wait=0.3) # close pop-up

def locateAmexWindow(driver):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:   amexLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1) 
    closeAmexPopUps(driver)
        
def amexLogin(driver):
    driver.openNewWindow('https://www.americanexpress.com/en-us/account/login?inav=iNavLnkLog')
    # driver.getElementAndSendKeys('id', "eliloUserID", getUsername('Amex'))
    # driver.getElementAndSendKeys('id', "eliloPassword", getPassword('Amex'))
    driver.getElementAndClick('id', "loginSubmit")
    # time.sleep(1)
    driver.getElementAndClick('xpath', "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span", wait=2) # close pop-up
    # time.sleep(1)

def clickViewAmexTransactions(driver):
    driver.getElementAndClick('link_text', "View Transactions", allowFail=False) # view transactions

def clickAmexHome(driver):
    driver.getElementAndClick('link_text', "Home", allowFail=False)

def getAmexBalance(driver):
    locateAmexWindow(driver)
    if 'activity' not in driver.webDriver.current_url:
        clickAmexHome(driver)
        clickViewAmexTransactions(driver)
    balance = driver.getElementText('xpath', "/html/body/div[1]/div/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[1]/div/div/section/div[2]/div[5]/div[3]/span[1]", allowFail=False)
    return balance.replace('$', '') if balance else False

def exportAmexTransactions(driver):
    if 'activity' not in driver.webDriver.current_url:
        clickAmexHome(driver)
        clickViewAmexTransactions(driver)
    driver.getElementAndClick('xpath', "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span", wait=2) # view activity
    # time.sleep(6)
    driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/button/div/i", wait=7, allowFail=False) # download arrow
    num = 1
    while True:
        fileTypeElement = driver.getElement('xpath', f"//*[@id='root']/div/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div/div/div[2]/div/div/div[1]/div/fieldset/div[{str(num)}]/label")
        if fileTypeElement.text == 'CSV':
            fileTypeElement.click()
            break
        else: num +=1
    try: os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:   exception = "caught"
    driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div/div/div[3]/div/a/span") # Download
    time.sleep(3)

def claimAmexRewards(driver, account):
    locateAmexWindow(driver)   
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    rawBalance = driver.getElementText('id', 'globalmrnavpointbalance')
    if rawBalance:
        rewardsBalance = rawBalance.replace('$', '')
        if float(rewardsBalance) > 0:
            driver.getElementAndClick('xpath', "//*[@id='recommendations-CTA']/a", wait=2) # redeem now link
            rewardsInputElement = driver.getElement('id', 'rewardsInput')
            if rewardsInputElement:
                rewardsInputElement.send_keys(rewardsBalance)
                rewardsInputElement.send_keys(Keys.TAB)
                driver.getElementAndClick('xpath', "//*[@id='continue-btn']/span")
                if driver.getElementAndClick('xpath', "//*[@id='use-dollars-btn']/span"):
                    # account.value = (float(account.balance) - float(rewardsBalance))*-1
                    return True
    return False

def importAmexTransactions(account, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(r'C:\Users\dmagn\Downloads\activity.csv'), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[1]
        description = rawDescription
        amount = -Decimal(row[2])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "AUTOPAY PAYMENT" in rawDescription.upper():                             
            continue
        elif "YOUR CASH REWARD/REFUND IS" in rawDescription.upper():                
            description = "Amex CC Rewards"
            toAccount = book.getGnuAccountFullName('Credit Card Rewards')
        elif "BP#" in rawDescription.upper():                         
            toAccount = book.getGnuAccountFullName('Transportation') + ':Gas'
        elif 'PICK N SAVE' in rawDescription.upper():
            toAccount = book.getGnuAccountFullName('Groceries')
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runAmex(driver, account, book):
    locateAmexWindow(driver)
    account.setBalance(getAmexBalance(driver))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    exportAmexTransactions(driver)
    claimAmexRewards(driver, account)
    importAmexTransactions(account, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

if __name__ == '__main__':
    driver = Driver("Chrome")
    # book = GnuCash('Finance')
    # Amex = USD("Amex", book)
    locateAmexWindow(driver)
    # runAmex(driver, Amex, book)
    # Amex.getData()
    # book.closeBook()


    print(getAmexBalance(driver))