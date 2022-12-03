import os
import time
from datetime import datetime

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Discover":
    from Functions.GeneralFunctions import (getPassword, setDirectory, showMessage)
    from Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Classes.WebDriver import Driver
else:
    from .Functions.GeneralFunctions import (getPassword, setDirectory, showMessage)
    from .Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet

def locateDiscoverWindow(driver):
    found = driver.findWindowByUrl("discover.com")
    if not found:
        discoverLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def discoverLogin(driver):
    directory = setDirectory()    
    driver.execute_script("window.open('https://portal.discover.com/customersvcs/universalLogin/ac_main');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])    
    # login
    # username already entered
    # driver.find_element(By.ID, 'userid-content').send_keys(getUsername(directory, 'Discover'))
    driver.find_element(By.ID, 'password-content').send_keys(getPassword(directory, 'Discover'))
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[1]/div/form/input[8]').click()

    #handle pop-up
    try:
        driver.find_element(By.XPATH, "//*[@id='root']/div[4]/div/div/button/img").click()
    except (NoSuchElementException, ElementNotInteractableException, AttributeError):
        exception = "caught"

def getDiscoverBalance(driver):
    locateDiscoverWindow(driver)
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/statements/app/activity#/current")
    time.sleep(1)
    return driver.webDriver.find_element(By.ID, "new-balance").text.strip('$')

def exportDiscoverTransactions(driver, today):
    # Click on Download
    driver.find_element(By.XPATH, "//*[@id='current-statement']/div[1]/div/a[2]").click()
    # CLick on CSV
    driver.find_element(By.ID, "radio4").click()
    # CLick Download
    driver.find_element(By.ID, "submitDownload").click()
    # Click Close
    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[5]/div/form/div/div[4]/a[1]").click()
    year = today.year
    stmtYear = str(year)
    stmtMonth = today.strftime('%m')
    return r"C:\Users\dmagn\Downloads\Discover-Statement-" + stmtYear + stmtMonth + "12.csv"

def claimDiscoverRewards(driver):
    locateDiscoverWindow(driver)    
    driver.webDriver.get("https://card.discover.com/cardmembersvcs/rewards/app/redemption?ICMPGN=AC_NAV_L3_REDEEM#/cash")
    try:
        # Click Electronic Deposit to your bank account
        driver.webDriver.find_element(By.ID, "electronic-deposit").click()
        time.sleep(1)
        # Click Redeem All link
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/form/div[2]/fieldset/div[3]/div[2]/span[2]/button").click()
        time.sleep(1)
        # Click Continue
        driver.webDriver.find_element(By.XPATH, "//*[@id='cashbackForm']/div[4]/input").click()
        time.sleep(1)
        # Click Submit
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div/div/section/div[2]/div/div/div/div[1]/div/div/div[2]/div/button[1]").click()
    except (NoSuchElementException, ElementClickInterceptedException):
        exception = "caught"

def locateAndUpdateSpreadsheetForDiscover(driver, discover, today):
    directory = setDirectory()    
    # switch worksheets if running in December (to next year's worksheet)
    month = today.month
    year = today.year
    if month == 12:
        year = year + 1
    discoverNeg = float(discover.strip('$')) * -1
    updateSpreadsheet(directory, 'Checking Balance', year, 'Discover', month, discoverNeg, 'Discover CC')
    updateSpreadsheet(directory, 'Checking Balance', year, 'Discover', month, discoverNeg, 'Discover CC', True)
    # Display Checking Balance spreadsheet
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=1688093622');")

def runDiscover(driver):
    directory = setDirectory()    
    locateDiscoverWindow(driver)
    discover = getDiscoverBalance(driver)
    today = datetime.today()
    transactionsCSV = exportDiscoverTransactions(driver.webDriver, today)
    claimDiscoverRewards(driver)
    myBook = openGnuCashBook('Finance', False, False)
    reviewTrans = importGnuTransaction('Discover', transactionsCSV, myBook, driver.webDriver, directory)
    discoverGnu = getGnuCashBalance(myBook, 'Discover')
    locateAndUpdateSpreadsheetForDiscover(driver.webDriver, discover, today)
    if reviewTrans:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    showMessage("Balances + Review", f'Discover Balance: {discover} \n' f'GnuCash Discover Balance: {discoverGnu} \n \n' f'Review transactions:\n{reviewTrans}')
    driver.close()

if __name__ == '__main__':
    driver = Driver("Chrome")
    runDiscover(driver)
