import os
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, getUsername)
    from Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI, openGnuCashBook
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword, getUsername)
    from .Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI, openGnuCashBook

def getAmexBasePath():
    return '/html/body/div[1]/div[2]/div[3]/div/div/div/div/div[2]/div/div[2]/div/div/'
            
def locateAmexWindow(driver):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:
        amexLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1) 
        
def amexLogin(driver):
    driver.openNewWindow('https://www.americanexpress.com/')
    driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/header/div[2]/div[1]/div[3]/div/div[5]/ul/li[3]/span/a[1]").click()
    driver.webDriver.find_element(By.ID, "eliloUserID").send_keys(getUsername('Amex'))
    driver.webDriver.find_element(By.ID, "eliloPassword").send_keys(getPassword('Amex'))
    driver.webDriver.find_element(By.ID, "loginSubmit").click()
    # handle pop-up
    try:
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span").click()
    except NoSuchElementException:
        exception = "caught"
    time.sleep(1)

def getAmexBalance(driver):
    locateAmexWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[1]/div[1]/div/div[1]/div/div/span[1]/div").text.replace('$', '')

def exportAmexTransactions(driver):
    # click view transactions
    driver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[2]/div[2]/div/div[1]/div[1]/div/a").click()
    try: 
        # click on View Activity (for previous billing period)
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span").click()
    except NoSuchElementException:
        exception = "caught"
    # click on Download
    time.sleep(5)
    driver.find_element(By.XPATH, getAmexBasePath() + "table/thead/div/tr[1]/td[2]/div/div[2]/button/button").click()
    # click on CSV option
    driver.find_element(By.XPATH, getAmexBasePath() + "div[2]/div/div/div/div/div/div[1]/div/div/div[1]/div/fieldset/div[1]/label").click()
    # delete old csv file, if present
    try:
        os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:
        exception = "caught"
    # click on Download
    driver.find_element(By.XPATH, getAmexBasePath() + "div[2]/div/div/div/div/div/div[2]/div/a").click()
    time.sleep(3)

def claimAmexRewards(driver):
    locateAmexWindow(driver)   
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    rewardsBalance = driver.webDriver.find_element(By.ID, "globalmrnavpointbalance").text.replace('$', '')
    if float(rewardsBalance) > 0:
        driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(rewardsBalance)
        driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(Keys.TAB)
        driver.webDriver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
        driver.webDriver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()

def runAmex(driver, account, book):
    locateAmexWindow(driver)
    account.setBalance(getAmexBalance(driver))
    exportAmexTransactions(driver.webDriver)
    claimAmexRewards(driver)
    importGnuTransaction(account, r'C:\Users\dmagn\Downloads\activity.csv', driver.webDriver, book)
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:
        openGnuCashUI('Finances')

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = openGnuCashBook('Finance', False, False)
    Amex = USD("Amex", book)    
    runAmex(driver, Amex, book)
    Amex.getData()
    if not book.is_saved:
        book.save()
    book.close()