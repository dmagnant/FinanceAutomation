import os, time, csv
from decimal import Decimal
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException 
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername, getStartAndEndOfDateRange)

def getAmexBasePath():  return '/html/body/div[1]/div[2]/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div'
            
def locateAmexWindow(driver):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:   amexLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1) 
        
def amexLogin(driver):
    driver.openNewWindow('https://www.americanexpress.com/en-us/account/login?inav=iNavLnkLog')
    # driver.webDriver.find_element(By.ID, "eliloUserID").send_keys(getUsername('Amex'))
    # driver.webDriver.find_element(By.ID, "eliloPassword").send_keys(getPassword('Amex'))
    driver.webDriver.find_element(By.ID, "loginSubmit").click()
    try: driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span").click() # close pop-up
    except NoSuchElementException:  exception = "caught"
    time.sleep(1)

def clickViewAmexTransactions(driver):
    driver.webDriver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[3]/div[2]/div/div[1]/div[1]/div/a").click() # view transactions

def clickAmexHome(driver):
    driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/section/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/div/div/div[1]/div/div[1]/div/ul/li[1]/a/span").click() # Home

def getAmexBalance(driver):
    locateAmexWindow(driver)
    if 'activity' not in driver.webDriver.current_url:
        clickAmexHome(driver)
        clickViewAmexTransactions(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='root']/div[2]/main/section/div[3]/div/div/div/div/div/div/div[2]/div/div[1]/div/div/section/div[2]/div[5]/div[3]").text.replace('$', '')

def exportAmexTransactions(driver):
    if 'activity' not in driver.webDriver.current_url:
        clickAmexHome(driver)
        clickViewAmexTransactions(driver)
    try: driver.webDriver.find_element(By.XPATH, "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span").click() # view activity
    except NoSuchElementException:exception = "caught"
    time.sleep(6) 
    driver.webDriver.find_element(By.XPATH, getAmexBasePath() + "/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/button/div/p").click() # download arrow
    num = 1
    while True:
        fileTypeElement = driver.webDriver.find_element(By.XPATH, getAmexBasePath() + "[1]/div/div/div/div/div/div[2]/div/div/div[1]/div/fieldset/div[" + str(num) + "]/label")
        if fileTypeElement.text == 'CSV':
            fileTypeElement.click()
            break
        else: num +=1
    try: os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:   exception = "caught"
    driver.webDriver.find_element(By.XPATH, getAmexBasePath() + "[1]/div/div/div/div/div/div[3]/div/a/span").click() # Download
    time.sleep(3)

def claimAmexRewards(driver, account):
    locateAmexWindow(driver)   
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    try:
        rewardsBalance = driver.getIDElementTextOnceAvailable('globalmrnavpointbalance').replace('$', '')
        if float(rewardsBalance) > 0:
            driver.webDriver.find_element(By.XPATH,"//*[@id='recommendations-CTA']/a").click() # redeem now link
            rewardsInputElement = driver.getIDElementOnceAvailable('rewardsInput')
            rewardsInputElement.send_keys(rewardsBalance)
            rewardsInputElement.send_keys(Keys.TAB)
            # driver.webDriver.execute_script("window.scrollTo(0, 1300)")
            driver.webDriver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
            driver.webDriver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()
        account.setValue(float(rewardsBalance))
    except StaleElementReferenceException: exception = 'rewards likely already redeemed'
    if account.value:
        account.value = float(account.balance) - account.value

def importAmexTransactions(account, book, gnuCashTransactions):
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
        elif "YOUR CASH REWARD/REFUND IS" in rawDescription.upper():                description = "Amex CC Rewards"
        else:                                                                       description = rawDescription
        toAccount = book.getGnuAccountFullName(fromAccount, description=description)
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

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     Amex = USD("Amex", book)
#     runAmex(driver, Amex, book)
#     Amex.getData()
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    # book = GnuCash('Finance')
    # Amex = USD("Amex", book)
    # Amex.setBalance(getAmexBalance(driver))
    # claimAmexRewards(driver, Amex)

    locateAmexWindow(driver)
    driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(float(1.01))
    driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(Keys.TAB)
    time.sleep(1)
    driver.webDriver.execute_script("window.scrollTo(0, 1300)")
    driver.webDriver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
    driver.webDriver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()

