import time, csv
from decimal import Decimal
from datetime import datetime

if __name__ == '__main__' or __name__ == "Discover":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash    
    from Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange, getUsername
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange, getUsername

def locateDiscoverWindow(driver):
    found = driver.findWindowByUrl("discover.com")
    if not found:   discoverLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def discoverLogin(driver):
    driver.openNewWindow('https://portal.discover.com/customersvcs/universalLogin/ac_main') 
    # login
    # username already entered
    # driver.getElementAndSendKeys('id', 'userid-content',getUsername('Discover'))
    # driver.getElementAndSendKeys('id', 'password-content',getPassword('Discover'))
    # time.sleep(1)
    driver.getElementAndClick('xpath', '/html/body/div[1]/div/div/main/div/div/div/div/login-card-wc/div/form/div/div[4]/button') # Log In
    driver.getElementAndClick('xpath', "//*[@id='root']/div[4]/div/div/button/img", wait=2) # handle pop-up

def getDiscoverBalance(driver):
    locateDiscoverWindow(driver)
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/statements/app/activity#/current")
    time.sleep(1)
    rawBalance = driver.getElementText('id', 'new-balance', allowFail=False)
    if rawBalance:
        return rawBalance.strip('$')
    return False

def exportDiscoverTransactions(driver, today):
    driver.getElementAndClick('xpath', "//*[@id='current-statement']/div[1]/div/a[2]") # download
    driver.getElementAndClick('id', "radio4") # csv
    driver.getElementAndClick('id', "submitDownload") # download
    driver.getElementAndClick('xpath', "//*[@id='downloadForm']/div/div[4]/a[1]/i") # x to close
    stmtYear, stmtMonth = str(today.year), today.strftime('%m')
    return r"C:\Users\dmagn\Downloads\Discover-Statement-" + stmtYear + stmtMonth + "12.csv"

def claimDiscoverRewards(driver, account):
    locateDiscoverWindow(driver)    
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/rewards/app/redemption?ICMPGN=AC_NAV_L3_REDEEM#/cash")
    rawBalance = driver.getElementText('xpath', "//*[@id='main-content-rwd']/div/div/div[1]/section[2]/div/div/span", allowFail=False)
    if rawBalance:
        balance = float(rawBalance.replace(' Available', '').replace('$',''))
    if balance > 0:
        driver.getElementAndClick('id', "electronic-deposit") # Electronic Deposit to your bank account
        # time.sleep(1)
        driver.getElementAndClick('xpath', "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/form/div[2]/fieldset/div[3]/div[2]/span[2]/button") # Redeem All link
        # time.sleep(1)
        driver.getElementAndClick('xpath', "//*[@id='cashbackForm']/div[4]/input") # Continue
        # time.sleep(1)
        driver.getElementAndClick('xpath', "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/div/div/div[1]/div/div/div[2]/div/button[1]") # Submit
    account.setValue(balance)
    if account.value:   account.value = account.balance - account.value
    print('balance: ' + str(account.balance))
    print('value: ' + str(account.value))

def importDiscoverTransactions(account, discoverActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num=0
    for row in csv.reader(open(discoverActivity), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[1], '%m/%d/%Y').date()
        rawDescription = row[2]
        description = rawDescription        
        amount = -Decimal(row[3])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "DIRECTPAY FULL BALANCE" in rawDescription.upper():                  
            continue
        elif "AUTOMATIC STATEMENT CREDIT" in rawDescription.upper():
            description = "Discover CC Rewards"
            toAccount = book.getGnuAccountFullName('CC Rewards')
        elif "BP#" in rawDescription.upper():                         
            toAccount = book.getGnuAccountFullName('Transportation') + ':Gas'
        if toAccount == 'Expenses:Other':
            for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET', 'MINI MARKET MILWAUKEE', 'KAINTH']:
                if i in rawDescription.upper():                        
                    toAccount = book.getGnuAccountFullName('Groceries')
                    break
        # toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        if toAccount == 'Expenses:Other': reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runDiscover(driver, account, book):
    today = datetime.today()
    locateDiscoverWindow(driver)
    account.setBalance(getDiscoverBalance(driver))
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    discoverActivity = exportDiscoverTransactions(driver, today)
    claimDiscoverRewards(driver, account)
    importDiscoverTransactions(account, discoverActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions: book.openGnuCashUI()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Discover = USD("Discover", book)
    runDiscover(driver, Discover, book)
    Discover.getData()
    book.closeBook()

    