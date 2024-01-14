import os
import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername)

def getAmexBasePath():
    return '/html/body/div[1]/div[2]/main/div/div/div/div/div[2]/div/div[2]/div/div/div'
            
            
def locateAmexWindow(driver):
    found = driver.findWindowByUrl("americanexpress.com")
    if not found:
        amexLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1) 
        
def amexLogin(driver):
    driver.openNewWindow('https://www.americanexpress.com/en-us/account/login?inav=iNavLnkLog')
    # driver.webDriver.find_element(By.ID, "eliloUserID").send_keys(getUsername('Amex'))
    # driver.webDriver.find_element(By.ID, "eliloPassword").send_keys(getPassword('Amex'))
    driver.webDriver.find_element(By.ID, "loginSubmit").click()
    try: # handle pop-up
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span").click()
    except NoSuchElementException:
        exception = "caught"
    time.sleep(1)

def getAmexBalance(driver):
    locateAmexWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[1]/div[1]/div/div[1]/div/div/span[1]/div").text.replace('$', '')

def exportAmexTransactions(driver):
    driver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[2]/div[2]/div/div[1]/div[1]/div/a").click() # view transactions
    try: 
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span").click() # view activity
    except NoSuchElementException:
        exception = "caught"
    time.sleep(6)
    driver.find_element(By.XPATH, getAmexBasePath() + "/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/div/button/div/i").click() # download arrow
    driver.find_element(By.XPATH, getAmexBasePath() + "[1]/div/div/div/div/div/div[2]/div/div/div[1]/div/fieldset/div[1]/label").click() # CSV Option
    try: # delete old csv file
        os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:
        exception = "caught"
    # click on Download
    driver.find_element(By.XPATH, getAmexBasePath() + "[1]/div/div/div/div/div/div[3]/div/a").click()
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
    book.importGnuTransaction(account, r'C:\Users\dmagn\Downloads\activity.csv', driver)
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:
        book.openGnuCashUI()

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Amex = USD("Amex", book)    
    runAmex(driver, Amex, book)
    Amex.getData()
    book.closeBook()