import time
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Worthy":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword, getUsername)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword, getUsername)

def locateWorthyWindow(driver):
    found = driver.findWindowByUrl("worthy.capital")
    if not found:
        worthyLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)

def worthyLogin(driver):
    driver.openNewWindow('https://worthy.capital/auth/login/')
    driver = driver.webDriver
    time.sleep(1)
    try:
        # driver.find_element(By.ID, "email").send_keys(getUsername('Worthy'))
        # driver.find_element(By.ID, "password").send_keys(getPassword('Worthy'))
        driver.find_element(By.XPATH, "//*[@id='__next']/div/div/main/div/form/div[3]/button").click() # sign in
    except NoSuchElementException:  exception = "already logged in"
    time.sleep(3)

def getWorthyBalance(driver, account):
    locateWorthyWindow(driver)
    time.sleep(1)
    worthy1Balance = driver.webDriver.find_element(By.XPATH, "//*[@id='__next']/div/div/main/div/div/div[1]/div/div/p/strong").text.strip('$').replace(',','').replace('*', '')
    account.setBalance(float(Decimal(worthy1Balance)))

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')    
    Worthy = USD("Worthy", book)    
    getWorthyBalance(driver, Worthy)
    Worthy.getData()
    book.closeBook()
    