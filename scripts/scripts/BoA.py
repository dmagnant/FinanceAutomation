import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "BoA":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, showMessage, getAnswerForSecurityQuestion, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, showMessage, getAnswerForSecurityQuestion, getStartAndEndOfDateRange)

def locateBoAWindowAndOpenAccount(driver, account):
    found = driver.findWindowByUrl("secure.bankofamerica.com")
    if not found:   boALogin(driver, account)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
        
def boALogin(driver, account):
    def getUserNameElement():       return driver.getElement('id', "onlineId1")
    def getPassWordElement():       return driver.getElement('id', "passcode1")
    def clickLoginButton():         return driver.getElementAndClick('id', 'signIn')
    
    print(f'getting account: {account}')
    driver.openNewWindow('https://www.bankofamerica.com/')
    username = getUserNameElement()
    username.click()
    # username.send_keys(getUsername('BoA CC'))
    time.sleep(3)
    password = getPassWordElement()
    password.send_keys(getPassword('BoA CC'))
    clickLoginButton()
    if driver.getElement('id', "signin-message", wait=2):
        driver.getElementAndSendKeys('id', 'onlineId1', getUsername('BoA CC'))
        driver.getElementAndSendKeys('id', 'passcode1', getPassword('BoA CC'))
        clickLoginButton()
    if driver.getElementAndClick('xpath', "//*[@id='btnARContinue']/span[1]", wait=2): # ID verification
        showMessage("Get Verification Code", "Enter code, then click OK")
        driver.getElementAndClick('xpath', "//*[@id='yes-recognize']")
        driver.getElementAndClick('xpath', "//*[@id='continue-auth-number']/span")
    question = driver.getElementText('xpath', "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/div[2]/label", wait=2)
    if question:
        driver.getElementAndSendKeys('name', 'challengeQuestionAnswer', getAnswerForSecurityQuestion(question))
        driver.getElementAndClick('xpath', "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/fieldset/div[2]/div/div[1]/input")
        driver.getElementAndClick('xpath', "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/a[1]/span")
    driver.getElementAndClick('xpath', "//*[@id='sasi-overlay-module-modalClose']/span[1]", wait=2) # close pop-up
    partialLink = 'Travel Rewards Visa Signature - 8955' if 'Joint' in account else 'Customized Cash Rewards Visa Signature - 5700'
    driver.getElementAndClick('partial_link_text', partialLink)
    # time.sleep(3)

def getBoABalance(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    balance = driver.getElementText('xpath', "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[3]/div[5]/div[3]/div/div[2]/div[2]/div[2]")
    return balance.replace('$','').replace(',','') if balance else False

def exportBoATransactions(driver, account, today):
    driver.getElementAndClick('partial_link_text', "Previous transactions")
    driver.getElementAndClick('xpath', "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[1]/a") # download
    # time.sleep(1)
    driver.getElementAndSendKeys('xpath', "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[3]/div[1]/select", 'm') # for microsoft excel
    driver.webDriver.execute_script("window.scrollTo(0, 300)")
    driver.getElementLocateAndClick('xpath', "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[4]/div[2]/a/span") # download transactions
    stmtMonth, stmtYear = today.strftime("%B"), str(today.year)
    accountNum = "_8955.csv" if 'joint' in account else "_5700.csv"
    return os.path.join(r"C:\Users\dmagn\Downloads", stmtMonth + stmtYear + accountNum)

def claimBoARewards(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    if 'joint' in account:
        driver.getElementAndClick('xpath', "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[2]/a") # View/Redeem
        driver.getElementAndClick('id', 'redeemButton') # redeem points
        driver.switchToLastWindow()
        # time.sleep(1)
        driver.getElementAndClick('xpath', "/html/body/main/div/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]/a") # redeem
        rawAvailablePoints = driver.getElementText('id', 'zsummary_availablepoints', allowFail=False)
        if not rawAvailablePoints:
            return False
        availablePoints = rawAvailablePoints.replace(',','')
        if int(availablePoints) >= 2500:
            remainingPoints = availablePoints
            num = 1
            if int(availablePoints) > 0:
                while remainingPoints:
                    driver.getElementAndClick('xpath', "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[6]/label/input") # select to redeem
                    rawRemainingPoints = driver.getElementText('id', 'remainingpoints', allowFail=False)
                    if not rawRemainingPoints:
                        return False
                    remainingPoints = rawRemainingPoints.replace(',','')
                    num += 2
                    availablePoints = remainingPoints
                driver.getElementAndClick('xpath', "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]") # "enter points to redeem"
                backspaces = 8
                while backspaces > 0:
                    driver.getElementAndSendKeys('xpath', "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]", Keys.BACKSPACE)
                    backspaces -= 1
                driver.getElementAndSendKeys('xpath', "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]", availablePoints)
                driver.getElementAndClick('xpath', "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[3]") # update
                driver.getElementAndClick('xpath', "/html/body/main/div/div[2]/div/div[1]/div/div[2]/table/tbody/tr[7]/td/div/input") # request travel credit
                driver.getElementAndClick('xpath', "/html/body/div[2]/div[2]/div[1]/div[1]/div[4]/input[1]") # complete redemption
    else:
        driver.getElementAndClick('xpath', "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[3]/a") # View/Redeem
        time.sleep(5)
        driver.webDriver.execute_script("window.scrollTo(0, 300)")
        time.sleep(3)
        driver.getElementAndClick('id', 'choose-redeem-primary-button') # redeem cash rewards
        driver.getElementAndClick('xpath', "/html/body/div[1]/div/div/div[2]/div/div/button", wait=2) # close pop-up
        driver.findWindowByUrl("managerewardsonline.bankofamerica.com")
        driver.getElementAndClick('xpath', "//*[@id='skip-to-maincontent']/div/div/div/div/div/ul/li[1]/div/div[1]/div[2]/div/a") # get cash back
        driver.getElementAndClick('id', "redemption_option") # redemption option
        if driver.getElementAndSendKeys('id', "redemption_option", "v"): # for visa statement credit
            driver.getElementAndSendKeys('id', "redemption_option", Keys.ENTER)
            driver.getElementAndClick('id', "redeem-all") # redeem all
            driver.getElementAndClick('id', "complete-otr-confirm") # complete redemption

def importBoATransactions(account, boAActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num = 0
    for row in csv.reader(open(boAActivity), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
        rawDescription = row[2]
        description = rawDescription
        amount = Decimal(row[4])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "BA ELECTRONIC PAYMENT" in rawDescription.upper():                           
            continue
        elif 'AMAZON' in rawDescription.upper() or 'AMZN' in rawDescription.upper():
            toAccount = book.getGnuAccountFullName('Amazon')
        if toAccount == 'Expenses:Other':
            for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET', 'MINI MARKET MILWAUKEE', 'KAINTH']:
                if i in rawDescription.upper():                        
                    toAccount = book.getGnuAccountFullName('Groceries')
                    break
            for i in ['MCDONALD', 'JIMMY JOHN', 'COLECTIVO', "KOPP'S CUSTARD", 'MAHARAJA', 'STARBUCKS', 'TACO BELL']:
                if i in rawDescription.upper():                        
                    toAccount = book.getGnuAccountFullName("Bars & Restaurants")
                    break
        if toAccount == 'Expenses:Other':
            if account.name == 'BoA':
                if "CASH REWARDS STATEMENT CREDIT" in rawDescription.upper():
                    description = "BoA CC Rewards"
                    toAccount = book.getGnuAccountFullName('Credit Card Rewards')
            elif account.name == 'BoA-joint':
                if "HOMEDEPOT" in rawDescription.upper().replace(' ',''):
                    description = 'Home Depot'
                    toAccount = book.getGnuAccountFullName(description)
                elif "SPECTRUM" in rawDescription.upper():                                      
                    description = "Internet Bill"
                    toAccount = book.getGnuAccountFullName('Internet')
                elif 'TRAVEL CREDIT' in rawDescription.upper():                               
                    toAccount = 'Income:Credit Card Rewards'
                elif "GOOGLE FI" in description.upper() or "GOOGLE *FI" in description.upper():             
                    toAccount = book.getGnuAccountFullName('Phone')
                elif "MILWAUKEE ELECTRIC TO" in description:
                    toAccount = book.getGnuAccountFullName('Home Expenses') + ':Maintenance'
                elif 'UBER' in description.upper():
                    toAccount = book.getGnuAccountFullName('Travel') + ':Ride Services'
                elif 'CHEWY' in description.upper():
                    toAccount = book.getGnuAccountFullName('Pet')
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runBoA(driver, account, book):
    locateBoAWindowAndOpenAccount(driver, account.name)
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    account.setBalance(getBoABalance(driver, account.name))
    boAActivity = exportBoATransactions(driver, account.name, datetime.today())
    claimBoARewards(driver, account.name)
    importBoATransactions(account, boAActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()

# if __name__ == '__main__':
#     SET_ACCOUNT_VARIABLE = "BoA-joint" # BoA or BoA-joint
#     bookName = 'Finance' if SET_ACCOUNT_VARIABLE == 'Personal' else 'Home'
#     book = GnuCash(bookName)
#     driver = Driver("Chrome")
#     BoA = USD(SET_ACCOUNT_VARIABLE, book)
#     runBoA(driver, BoA, book)
#     BoA.getData()
#     book.closeBook()
    
if __name__ == '__main__':
    SET_ACCOUNT_VARIABLE = "BoA" # BoA or BoA-joint
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    account = USD(SET_ACCOUNT_VARIABLE, book)
    locateBoAWindowAndOpenAccount(driver, account.name)
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    account.setBalance(getBoABalance(driver, account.name))
    boAActivity = exportBoATransactions(driver, account.name, datetime.today())
    claimBoARewards(driver, account.name)
    importBoATransactions(account, boAActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()
    account.getData()