import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.Selenium import WebDriver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, getKeePassProperties, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, getKeePassProperties, getStartAndEndOfDateRange)

def getAmexAccounts(book):
    return {'Checking': USD("Business Checking", book), 'Personal': USD("Amex Personal", book), 'Business': USD("Amex Business", book)}

def closeAmexPopUps(driver):
    elementPath = '/html/body/div[1]/div/main/section/div[3]/div/div/div[1]/div/div/div/div/div/div/div/header/button/div/span[2]/svg'
    driver.getElementAndClick('xpath', elementPath, allowFail=True, wait=0.3) # close pop-up

def locateAmexWindowAndOpenAccount(driver, account):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:   amexLogin(driver, account)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1) 
    closeAmexPopUps(driver)
    openAmexAccount(driver, account)

def openAmexAccount(driver, account):
    if 'Business Checking' == account.name:
        suffix = getKeePassProperties('Amex', 'CheckingAccountKey')
        if suffix not in driver.webDriver.current_url:
            driver.webDriver.get(f'https://www.americanexpress.com/en-us/banking/business/checking/accounts/{suffix}')
    else:
        account = account.name.replace('Amex ', '')
        suffix = getKeePassProperties('Amex', account + 'AccountKey')
        if suffix not in driver.webDriver.current_url:
            driver.webDriver.get(f'https://global.americanexpress.com/dashboard?account_key={suffix}')

def amexLogin(driver, account):
    driver.openNewWindow('https://www.americanexpress.com/en-us/account/login?inav=iNavLnkLog')
    # driver.getElementAndSendKeys('id', "eliloUserID", getUsername('Amex'))
    # driver.getElementAndSendKeys('id', "eliloPassword", getPassword('Amex'))
    driver.getElementAndClick('id', "loginSubmit")
    # time.sleep(1)
    driver.getElementAndClick('xpath', "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span", wait=2) # close pop-up
    # time.sleep(1)
    driver.waitForWebURLToLoad('https://global.americanexpress.com')

def clickViewAmexTransactions(driver):
    driver.getElementAndClick('link_text', "View Transactions", allowFail=False) # view transactions

def clickAmexHome(driver):
    driver.getElementAndClick('link_text', "Home", wait=2, allowFail=False)

def getAmexBalance(driver, account):
    locateAmexWindowAndOpenAccount(driver, account)
    balance = False
    if account.name == 'Business Checking':
        print('HAVE TO CODE FOR THIS')
        balance = driver.getElementText('xpath', "/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div/main/div/div[2]/div[1]/div[1]/div[1]/div[2]/div/p/span", allowFail=False)
    else:
        balance = driver.getElementText('xpath', "/html/body/div[1]/div/main/section/div[3]/div/div/div/div/div[2]/div/div/div/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/span[1]/h1/span[1]", allowFail=False)                                                                                
    return balance.replace('$', '').replace(',','') if balance else False

def exportAmexTransactions(driver):
    if 'activity' not in driver.webDriver.current_url:
        clickAmexHome(driver)
        clickViewAmexTransactions(driver)
    driver.getElementAndClick('xpath', "//*[@data-testid='feed-download-button']", wait=2, allowFail=False) # download button in pop-up
    num = 1
    while True:
        fileTypeElement = driver.getElement('xpath', f"/html/body/div[1]/div/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div/div[2]/div/div/div/div/fieldset/div[{str(num)}]/label")
        if fileTypeElement.text == 'CSV':
            fileTypeElement.click()
            break
        else: num +=1
    try: os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:   pass
    driver.randomSleep(1,3)
    if not driver.getElementAndClick('css_selector', 'a[data-test-id="myca-activity-download-footer-download-confirm-link"]', wait=1, allowFail=False): # Download
        return False
    driver.randomSleep(1,3)
    return True

def claimAmexRewards(driver, account):
    locateAmexWindowAndOpenAccount(driver, account)   
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    rawBalance = driver.getElementText('id', 'globalmrnavpointbalance')
    if rawBalance:
        rewardsBalance = rawBalance.replace('$', '')
        if float(rewardsBalance) > 0:
            driver.getElementAndClick('xpath', "//*[@id='recommendations-CTA']/a", wait=2) # redeem now link
            rewardsInputElement = driver.getElement('id', 'rewardsInput')
            if rewardsInputElement:
                driver.sendKeysToElement(rewardsInputElement, 'rewardsInput', rewardsBalance)
                driver.sendKeysToElement(rewardsInputElement, 'rewardsInput', Keys.TAB)
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
        # Check which format the row is in
        if len(row) > 5:  # Original format with 6 columns
            rawDescription = row[2]
            amount = -Decimal(row[5])
        else:  # New format with 3 columns
            rawDescription = row[1]
            amount = -Decimal(row[2])
        description = rawDescription
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "AUTOPAY PAYMENT" in rawDescription.upper():                             
            continue
        elif "YOUR CASH REWARD/REFUND IS" in rawDescription.upper():                
            description = "Amex CC Rewards"
            toAccount = book.getGnuAccountFullName('Credit Card Rewards')
        elif "BP#" in rawDescription.upper():                         
            toAccount = book.getGnuAccountFullName('Transportation') + ':Gas'
        elif 'PICK N SAVE' in rawDescription.upper() or 'KETTLE RANGE' in rawDescription.upper():
            toAccount = book.getGnuAccountFullName('Groceries')
        if 'Other' in toAccount:   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runAmexCC(driver, account, book):
    locateAmexWindowAndOpenAccount(driver, account)
    account.setBalance(getAmexBalance(driver, account))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    if not exportAmexTransactions(driver):
        print('failed to export amex transactions')
        return False
    claimAmexRewards(driver, account)
    importAmexTransactions(account, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    if 'Personal' in account.name:
        account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

if __name__ == '__main__':
    driver = WebDriver("Chrome")
    # book = GnuCash('Finance')
    # accounts = getAmexAccounts(book)

    # runAmex(driver, Amex, book)
    # Amex.getData()
   

    driver.findWindowByUrl("americanexpress.com")
    exportAmexTransactions(driver)
