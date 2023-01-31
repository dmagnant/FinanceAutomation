import time

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Midas":
    from Classes.Asset import Crypto
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import getOTP  
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import getOTP    

def locateMidasWindow(driver):
    found = driver.findWindowByUrl("app.midas.investments")
    if not found:
        midasLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def midasLogin(driver):
    driver.openNewWindow('https://app.midas.investments/?login=true&&')
    driver = driver.webDriver
    try: 
        # click Google
        driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[1]/div[2]/div/div/button[1]").click()
        # time.sleep(3)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        token = getOTP('midas')
        driver.find_element(By.ID, "input").send_keys(token)
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    except (NoSuchElementException, StaleElementReferenceException):
        exception = "already logged in"

def getMidasBalances(driver, coinList):
    locateMidasWindow(driver)    
    driver.webDriver.get("https://midas.investments/assets")
    for coin in coinList:
        coinBalance = float(driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/ul/li[1]/div/div[3]/div[1]/span[2]").text.replace(coin.symbol, ''))
        coin.setBalance(coinBalance)
    return coinList

def runMidas(driver):
    locateMidasWindow(driver)
    Bitcoin = Crypto("Bitcoin")
    Ethereum = Crypto("Ethereum")
    coinList = getMidasBalances(driver, [Bitcoin, Ethereum])
    for coin in coinList:
        account = coin.symbol + "-Midas"
        coin.updateSpreadsheetAndGnuCash(account)
    return coinList

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runMidas(driver)
    for coin in response:
        coin.getData()

