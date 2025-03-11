import time, pyautogui, csv
from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Chase":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, getPassword, getStartAndEndOfDateRange

else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, getPassword, getStartAndEndOfDateRange


def locateChaseWindow(driver):
    found = driver.findWindowByUrl("chase.com/web/auth")
    if not found:   chaseLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def activateChaseWindow(title):
    for w in pyautogui.getWindowsWithTitle("Google Chrome"):
        if title in w.title.lower(): w.activate()

def chaseLogin(driver):
    driver.openNewWindow('https://secure.chase.com/web/auth/#/logon/logon/chaseOnline?treatment=chase&lang=en')
    time.sleep(5)
    activateChaseWindow("sign in - chase.com")
    n=1
    while n<=8: pyautogui.press('tab'); n+=1
    if not driver.getElementAndClick('id', 'signin-button'): # Sign In 
        pyautogui.press('enter')
    if driver.getElementAndClick('id', "simplerAuth-dropdownoptions-styledselect"):
        driver.getElementAndClick('id', "container-1-simplerAuth-dropdownoptions-styledselect")
        driver.getElementAndClick('id', "requestIdentificationCode-sm")
        time.sleep(3)
        driver.getElementAndSendKeys('id', "password_input-input-field", getPassword('Chase')) # chase password
        showMessage('Device Verification', 'Enter Code From Phone, Press Enter')
        driver.getElementAndClick('id', "log_on_to_landing_page-sm") # Next

def getChaseBalance(driver):
    locateChaseWindow(driver)    
    rawBalance = driver.getElementText('xpath', "//*[@id='818208017-lastStatementBalance-dataItem']/div[2]", allowFail=False)
    if rawBalance:
        return rawBalance.strip('$')
    return False

def exportChaseTransactions(driver, today):
    driver.webDriver.get("https://secure.chase.com/web/auth/dashboard#/dashboard/transactions/818208017/CARD/BAC")
    time.sleep(3)
    activateChaseWindow("transactions - chase")
    driver.getElementAndClick('id', 'ACTIVITY-header-selector-label') # Activity Since Last Statement
    pyautogui.press('down');    pyautogui.press('down'); pyautogui.press('down'); pyautogui.press('down'); pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1)
    driver.getElementAndClick('id', "quick-action-download-activity-tooltip") # Download
    time.sleep(1)
    driver.getElementAndClick('id', "download") # Download
    monthFrom = "12"               if today.month == 1 else "{:02d}".format(today.month - 1)
    yearfrom = str(today.year - 1) if today.month == 1 else str(today.year)
    fromDate = yearfrom + monthFrom + "07_"
    toDate = str(today.year) + today.strftime('%m') + "06_"
    currentDate = str(today.year) + today.strftime('%m') + today.strftime('%d')
    return r'C:\Users\dmagn\Downloads\Chase2715_Activity' + fromDate + toDate + currentDate + '.csv'

def claimChaseRewards(driver):
    locateChaseWindow(driver)
    time.sleep(1)
    driver.webDriver.get("https://ultimaterewardspoints.chase.com/cash-back?lang=en")
    time.sleep(2)
    activateChaseWindow("ultimate rewards - chase")
    balance = driver.getElementText('xpath', "//*[@id='pointsBalanceId']/div/span[1]", allowFail=False)
    if float(balance) > 0:
        n=1
        while n<=12:
            pyautogui.press('tab'); time.sleep(1);  n+=1
        for num in balance: pyautogui.press(num)
        pyautogui.press('tab'); pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('space')
        pyautogui.press('tab'); pyautogui.press('tab')
        pyautogui.press('space')
        time.sleep(3)
        n=1
        while n<=12:
            pyautogui.press('tab'); time.sleep(1);  n+=1
        time.sleep(1)
        pyautogui.press('space') # submit

def importChaseTransactions(account, chaseActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    num = 0
    for row in csv.reader(open(chaseActivity), delimiter=','):
        reviewTransaction = False
        if num <1: num+=1; continue # skip header
        postDate = datetime.strptime(row[1], '%m/%d/%Y').date()
        rawDescription = row[2]
        description = rawDescription
        transactionType = row[3]        
        amount = Decimal(row[5])
        fromAccount = account.gnuAccount
        toAccount = book.getGnuAccountFullName('Other')
        if "AUTOMATIC PAYMENT" in rawDescription.upper():                           
            continue
        elif "REDEMPTION CREDIT" in rawDescription.upper() and float(amount) > 0:   
            description = "Chase CC Rewards"
            toAccount = book.getGnuAccountFullName('CC Rewards')  
        elif "BP#" in rawDescription.upper():                         
            toAccount = book.getGnuAccountFullName('Transportation') + ':Gas'            
        elif transactionType == "Food & Drink":   
            toAccount = book.getGnuAccountFullName('Bars & Restaurants')
        elif transactionType == 'Groceries':    
            toAccount = book.getGnuAccountFullName('Groceries')
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runChase(driver, account, book):
    locateChaseWindow(driver)
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    account.setBalance(getChaseBalance(driver))
    chaseActivity = exportChaseTransactions(driver, datetime.today())
    claimChaseRewards(driver)
    importChaseTransactions(account, chaseActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:  book.openGnuCashUI()
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Chase = USD("Chase", book)    
    runChase(driver, Chase, book)
    Chase.getData()
    book.closeBook()
    
# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     Chase = USD("Chase", book)
#     chaseLogin(driver)




