import os, time, csv
from datetime import datetime
from decimal import Decimal
from selenium.webdriver.common.keys import Keys

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
    # Login
    # driver.getElementAndSendKeys('id', 'username', getUsername('Barclay Card'))
    driver.getElementAndSendKeys('id', 'password', getPassword('Barclay Card'))
    driver.getElementAndClick('id', 'loginButton')
    # handle security questions
    question1 = driver.getElementText('id', 'question1TxtbxLabel', wait=2)
    question2 = driver.getElementText('id', 'question2TxtbxLabel', wait=2)
    if (question1 and question2):
        q1 = "In what year was your mother born?"
        a1 = os.environ.get('MotherBirthYear')
        q2 = "What is the name of the first company you worked for?"
        a2 = os.environ.get('FirstEmployer')
        if question1 == q1:
            driver.getElementAndSendKeys('id', 'rsaAns1', a1)
            driver.getElementAndSendKeys('id', 'rsaAns2', a2)
        else:
            driver.getElementAndSendKeys('id', 'rsaAns1', a2)
            driver.getElementAndSendKeys('id', 'rsaAns2', a1)
        driver.getElementAndClick('id', 'rsaChallengeFormSubmitButton')
    # handle Confirm Your Identity
    if driver.getElementAndClick('xpath', "/html/body/section[2]/div[4]/div/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div/div/div[2]/div[1]/label/span", wait=2):
        driver.getElementAndClick('xpath', "//button[@type='submit']")
        # User pop-up to enter SecurPass Code
        showMessage("Get Code From Phone", "Enter in box, then click OK")
        driver.getElementAndClick('xpath', "//button[@type='submit']")
    driver.getElementAndClick('xpath', "/html/body/div[4]/div/button/span", wait=2) # close pop-up

def getBarclaysBalance(driver):
    locateBarclaysWindow(driver)
    balance = driver.getElementText('xpath', "//*[@id='accountTile']/div[2]/div/div[2]/div[1]/div", allowFail=False)
    return balance.strip('-').strip('$').replace(',', '') if balance else False

def getBarclaysRewardBalance(driver):
    locateBarclaysWindow(driver)
    balance = driver.getElementText('xpath', "//*[@id='rewardsTile']/div[2]/div/div[2]/div[1]/div", allowFail=False)
    return float(balance.strip('-').replace('$', '').replace(',', '')) if balance else False

def exportBarclaysTransactions(driver, today):
    driver.getElementAndClick('xpath', "/html/body/section[2]/div[1]/nav/div/ul/li[3]/a") # Activity & Statements
    driver.getElementAndClick('xpath', "/html/body/section[2]/div[1]/nav/div/ul/li[3]/ul/li/div/div[2]/ul/li[1]/a") # Transactions
    driver.getElementAndClick('xpath', "/html/body/section[2]/div[4]/div/div/div[3]/div[1]/div/div[2]/span/div/button/span[1]") # download
    year, month = today.year, today.month
    monthTo, yrTO, yearTo = str(month), str(year - 2000), str(year)
    if month == 1:  monthFrom, yrFROM, yearFrom = "12", str(year - 2001), str(year - 1)
    else:           monthFrom, yrFROM, yearFrom = str(month - 1), yrTO, yearTo
    # enter date_range
    driver.getElementAndSendKeys('id', 'downloadFromDate_input', monthFrom + "/05/" + yrFROM)
    driver.getElementAndSendKeys('id', 'downloadToDate_input', monthTo + "/04/" + yrTO)
    driver.getElementAndClick('xpath', "/html/body/div[3]/div[2]/div/div/div[2]/div/form/div[3]/div/button") # Download
    time.sleep(2)
    return r"C:\Users\dmagn\Downloads\CreditCard_" + yearFrom + monthFrom + "05_" + yearTo + monthTo + "04.csv"

def claimBarclaysRewards(driver):
    locateBarclaysWindow(driver)
    driver.webDriver.get('https://www.barclaycardus.com/servicing/rewardsHub?shopRewards') # rewards center
    driver.waitForWebPageLoad()
    driver.getElementAndClick('xpath', '//*[@id="SSO-CASHBACK-URL_LINK"]/a') # direct deposit / statement credit
    driver.waitForWebPageLoad()
    driver.getElementAndClick('id', 'redeem-continue') # continue
    driver.getElementAndClick('id', 'mor_dropDown0') # reward method
    driver.getElementAndSendKeys('id', 'mor_dropDown0', Keys.DOWN)
    driver.getElementAndSendKeys('id', 'mor_dropDown0', Keys.ENTER)
    driver.getElementAndClick('id', 'achModal-continue') # continue
    driver.getElementAndClick('id', 'redeem-continue') # redeem now

def importBarclaysTransactions(account, barclaysActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(barclaysActivity), delimiter=','):
        reviewTransaction = False
        if num <5: num+=1; continue # skip header lines
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[1]
        description = rawDescription
        amount = Decimal(row[3])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "PAYMENT RECEIVED" in rawDescription.upper():   
            continue
        elif "TECH WAY AUTO SERV" in rawDescription.upper():   
            toAccount = book.getGnuAccountFullName('Transportation') + ':Car Maintenance'
        elif "BP#" in rawDescription.upper():                         
            toAccount = book.getGnuAccountFullName('Transportation') + ':Gas'
        elif 'PROGRESSIVE' in rawDescription.upper():
            toAccount = book.getGnuAccountFullName('Transportation') + ':Car Insurance'
        elif "SPOTHERO" in rawDescription.upper() or 'PARKMOBILE' in rawDescription.upper():                      
            toAccount = book.getGnuAccountFullName('Transportation') + ':Parking'
        elif 'UBER' in rawDescription.upper() or 'LYFT' in rawDescription.upper():                     
            toAccount = book.getGnuAccountFullName('Transportation') + ':Ride Services'
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
    rewardsBalance = getBarclaysRewardBalance(driver)
    barclaysActivity = exportBarclaysTransactions(driver, today)
    if rewardsBalance >= float(50): claimBarclaysRewards(driver)
    importBarclaysTransactions(account, barclaysActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Barclays = USD("Barclays", book)    
    # runBarclays(driver, Barclays, book)
    # Barclays.getData()
    # book.closeBook()
    today = datetime.today()
    rewardsBalance = getBarclaysRewardBalance(driver)
    print(f'Rewards Balance: ${rewardsBalance}')
    if rewardsBalance >= float(50): claimBarclaysRewards(driver)
