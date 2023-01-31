import time
from datetime import datetime

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Discover":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, showMessage)
    from Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword, showMessage)
    from .Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI

def locateDiscoverWindow(driver):
    found = driver.findWindowByUrl("discover.com")
    if not found:
        discoverLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def discoverLogin(driver):
    driver.openNewWindow('https://portal.discover.com/customersvcs/universalLogin/ac_main') 
    # login
    # username already entered
    # driver.find_element(By.ID, 'userid-content').send_keys(getUsername('Discover'))
    driver.webDriver.find_element(By.ID, 'password-content').send_keys(getPassword('Discover'))
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH, '/html/body/div[1]/main/div/div[1]/div/form/input[8]').click()

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

def runDiscover(driver):
    today = datetime.today()
    Discover = USD("Discover")
    locateDiscoverWindow(driver)
    Discover.setBalance(getDiscoverBalance(driver))
    transactionsCSV = exportDiscoverTransactions(driver.webDriver, today)
    claimDiscoverRewards(driver)
    importGnuTransaction(Discover, transactionsCSV, driver.webDriver)
    Discover.locateAndUpdateSpreadsheet(driver)
    if Discover.reviewTransactions:
        openGnuCashUI('Finances')
    showMessage("Balances + Review", f'Discover Balance: {Discover.balance} \n' f'GnuCash Discover Balance: {Discover.gnuBalance} \n \n' f'Review transactions:\n{Discover.reviewTransactions}')
    driver.webDriver.close()

if __name__ == '__main__':
    driver = Driver("Chrome")
    runDiscover(driver)
