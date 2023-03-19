import time
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Worthy":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, getUsername, showMessage)    
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword, getUsername, showMessage)

def locateWorthyWindow(driver):
    found = driver.findWindowByUrl("worthy.capital")
    if not found:
        worthyLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)

def worthyLogin(driver):
    driver.openNewWindow('https://worthy.capital/start')
    driver = driver.webDriver
    time.sleep(1)
    try:
        # click Login button
        driver.find_element(By.XPATH, "//*[@id='q-app']/div/div[1]/div/div[2]/div/button[2]/span[2]/span").click()
        time.sleep(1)
        # click Login button (again)
        driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/button").click()
        try:
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-error-msg-email']/div")
            # enter credentials
            driver.find_element(By.ID, "1-email").send_keys(getUsername('Worthy'))
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/div/div[2]/div[2]/span/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/input").send_keys(getPassword('Worthy'))
            # click Login button (again)
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/button").click()
        except NoSuchElementException:
            exception = "credentials were auto-entered"
    except NoSuchElementException:
        exception = "already logged in"
    time.sleep(3)

def getWorthyBalance(driver, account):
    locateWorthyWindow(driver)
    worthy1Balance = driver.webDriver.find_element(By.XPATH, "//*[@id='q-app']/div/div[1]/main/div/div/div[2]/div/div[2]/div/div/div[3]/div/h4/span[3]").text.strip('$').replace(',','')
    account.setBalance(float(Decimal(worthy1Balance)))

if __name__ == '__main__':
    driver = Driver("Chrome")
    Worthy = USD("Worthy")    
    getWorthyBalance(driver, Worthy)
    Worthy.getData()
    