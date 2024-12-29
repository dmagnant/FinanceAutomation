import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
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
    def getUserNameElement():       return driver.webDriver.find_element(By.ID, "onlineId1")
    def getPassWordElement():       return driver.webDriver.find_element(By.ID,"passcode1")
    def getSignInErrorMessage():    return driver.webDriver.find_element(By.ID,"signin-message")
    def clickLoginButton():         driver.webDriver.find_element(By.ID,'signIn').click()
    
    driver.openNewWindow('https://www.bankofamerica.com/')
    username = getUserNameElement()
    username.click()
    time.sleep(3)
    password = getPassWordElement()
    password.send_keys(getPassword('BoA CC'))
    clickLoginButton()
    try:    
        getSignInErrorMessage()
        driver.webDriver.find_element(By.ID, "onlineId1").send_keys(getUsername('BoA CC'))
        driver.webDriver.find_element(By.ID, "passcode1").send_keys(getPassword('BoA CC'))
        clickLoginButton()
    except  NoSuchElementException: exception = "good to proceed"
    try:     # handle ID verification
        driver.webDriver.find_element(By.XPATH, "//*[@id='btnARContinue']/span[1]").click()
        showMessage("Get Verification Code", "Enter code, then click OK")
        driver.webDriver.find_element(By.XPATH, "//*[@id='yes-recognize']").click()
        driver.webDriver.find_element(By.XPATH, "//*[@id='continue-auth-number']/span").click()
    except NoSuchElementException:  exception = "Caught"
    try:     # handle security questions
        question = driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/div[2]/label").text
        driver.webDriver.find_element(By.NAME, "challengeQuestionAnswer").send_keys(getAnswerForSecurityQuestion(question))
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/fieldset/div[2]/div/div[1]/input").click()
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/a[1]/span").click()
    except NoSuchElementException:  exception = "Caught"
    try:     driver.webDriver.find_element(By.XPATH, "//*[@id='sasi-overlay-module-modalClose']/span[1]").click() # close pop-up
    except NoSuchElementException:  exception = "Caught"
    partialLink = 'Travel Rewards Visa Signature - 8955' if 'joint' in account else 'Customized Cash Rewards Visa Signature - 5700'
    driver.webDriver.find_element(By.PARTIAL_LINK_TEXT, partialLink).click()
    time.sleep(3)

def getBoABalance(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[3]/div[5]/div[3]/div/div[2]/div[2]/div[2]").text.replace('$','').replace(',','')

def exportBoATransactions(driver, account, today):
    driver.find_element(By.PARTIAL_LINK_TEXT, "Previous transactions").click() # previous transactions
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[1]/a").click() # download
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[3]/div[1]/select").send_keys("m") # for microsoft excel
    driver.execute_script("window.scrollTo(0, 300)")
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[4]/div[2]/a/span").click() # download transactions
    stmtMonth, stmtYear = today.strftime("%B"), str(today.year)
    accountNum = "_8955.csv" if 'joint' in account else "_5700.csv"
    return os.path.join(r"C:\Users\dmagn\Downloads", stmtMonth + stmtYear + accountNum)

def claimBoARewards(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    if 'joint' in account:
        driver.webDriver.find_element(By.XPATH," /html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[2]/a").click() # view/redeem
        driver.clickIDElementOnceAvailable("redeemButton") # redeem points
        driver.switchToLastWindow()
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]/a").click() # redeem
        availablePoints = driver.webDriver.find_element(By.ID,"zsummary_availablepoints").text.replace(',','')
        if int(availablePoints) >= 2500:
            remainingPoints = availablePoints
            num = 1
            if int(availablePoints) > 0:
                while remainingPoints:
                    driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[6]/label/input").click() # select to redeem
                    remainingPoints = driver.webDriver.find_element(By.ID,"remainingpoints").text.replace(',','')
                    if remainingPoints == '':   break
                    num += 2
                    availablePoints = remainingPoints
                driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").click() # "enter points to redeem"
                backspaces = 8
                while backspaces > 0:
                    driver.webDriver.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").send_keys(Keys.BACKSPACE)
                    backspaces -= 1
                driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").send_keys(availablePoints)
                driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[3]").click() # update
                driver.webDriver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[1]/div/div[2]/table/tbody/tr[7]/td/div/input").click() # request travel credit
                driver.webDriver.find_element(By.XPATH,"/html/body/div[2]/div[2]/div[1]/div[1]/div[4]/input[1]").click() # complete redemption
    else:
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[3]/a").click() # View/Redeem menu
        time.sleep(5)
        driver.webDriver.execute_script("window.scrollTo(0, 300)")
        time.sleep(3)
        driver.clickIDElementOnceAvailable('rewardsRedeembtn') # redeem cash rewards
        driver.switchToLastWindow()
        try:    driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/button").click() # close pop-up
        except NoSuchElementException:  exception = "caught"
        driver.webDriver.find_element(By.XPATH, "//*[@id='skip-to-maincontent']/div/div/div[1]/div/div/ul/li[1]/div/div[1]/div[2]/div/a").click() # get cash back
        driver.webDriver.find_element(By.ID, "redemption_option").click() # redemption option
        try: # redeem if balance
            driver.webDriver.find_element(By.ID, "redemption_option").send_keys("v") # for visa statement credit
            driver.webDriver.find_element(By.ID, "redemption_option").send_keys(Keys.ENTER)
            driver.webDriver.find_element(By.ID, "redeem-all").click() # redeem all
            driver.webDriver.find_element(By.ID, "complete-otr-confirm").click() # compltete redemption
        except ElementNotInteractableException: exception = "caught"

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

        if toAccount != 'Expenses:Other':
            for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET', 'MINI MARKET MILWAUKEE', 'KAINTH']:
                if i in rawDescription.upper():                        
                    toAccount = book.getGnuAccountFullName('Groceries')
                    break
            for i in ['MCDONALD', 'JIMMY JOHN', 'COLECTIVO', "KOPP'S CUSTARD", 'MAHARAJA', 'STARBUCKS']:
                if i in rawDescription.upper():                        
                    toAccount = book.getGnuAccountFullName("Bars & Restaurants")
                    break
                
        if toAccount != 'Expenses:Other':
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
                    toAccount = book.getGnuAccountFullName('Home Expenses') + ':Home Maintenance'
                elif 'UBER' in description.upper():
                    toAccount = book.getGnuAccountFullName('Travel') + ':Ride Services'
                elif 'CHEWY' in description.upper():
                    toAccount = book.getGnuAccountFullName('Pet')
        # toAccount = book.getGnuAccountFullName(account.name, description=description)
        if toAccount == 'Expenses:Other':   reviewTransaction = True
        splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits, reviewTransaction=reviewTransaction)

def runBoA(driver, account, book):
    locateBoAWindowAndOpenAccount(driver, account.name)
    dateRange = getStartAndEndOfDateRange(timeSpan=60)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)    
    account.setBalance(getBoABalance(driver, account.name))
    boAActivity = exportBoATransactions(driver.webDriver, account.name, datetime.today())
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
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    BoA = USD('BoA', book)
    locateBoAWindowAndOpenAccount(driver, BoA)