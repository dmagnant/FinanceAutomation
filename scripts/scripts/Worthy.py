import time
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Worthy":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, getUsername,
                                            setDirectory, showMessage)    
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword, getUsername,
                                             setDirectory, showMessage)

def locateWorthyWindow(driver):
    found = driver.findWindowByUrl("worthy.capital")
    if not found:
        worthyLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)

def worthyLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://worthy.capital/start');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)
    try:
        # click Login button
        driver.find_element(By.XPATH, "//*[@id='q-app']/div/div[1]/div/div[2]/div/button[2]/span[2]/span").click()
        # click Login button (again)
        driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/button").click()
        try:
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-error-msg-email']/div")
            # enter credentials
            driver.find_element(By.ID, "1-email").send_keys(getUsername(directory, 'Worthy'))
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/div/div[2]/div[2]/span/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/input").send_keys(getPassword(directory, 'Worthy'))
            # click Login button (again)
            driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/button").click()
        except NoSuchElementException:
            exception = "credentials were auto-entered"
    except NoSuchElementException:
        exception = "already logged in"
    time.sleep(3)

def getWorthyBalance(driver):
    locateWorthyWindow(driver)
    Worthy = USD("Worthy")
    # Get balance from Worthy I
    worthy1BalanceElement = "//*[@id='q-app']/div/div[1]/main/div/div/div[2]/div/div[2]/div/div/div[3]/div/h4/span[3]"
    driver.webDriver.find_element(By.XPATH, worthy1BalanceElement).click()
    worthy1Balance = driver.webDriver.find_element(By.XPATH, worthy1BalanceElement).text.strip('$').replace(',','')
    Worthy.setBalance(float(Decimal(worthy1Balance)))
    return Worthy

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = getWorthyBalance(driver)
    response.getData()
    