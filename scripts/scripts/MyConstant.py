import time
from decimal import Decimal

import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "MyConstant":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getOTP, getUsername, getPassword)
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
    from Classes.Asset import Crypto
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getOTP, getUsername, getPassword)
    from .Functions.WebDriverFunctions import findWindowByUrl
    from .Classes.Asset import Crypto

def locateMyConstantWindow(driver):
    found = findWindowByUrl(driver, "www.myconstant.com")
    if not found:
        myConstantLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def myConstantLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.myconstant.com/log-in');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    #login
    try:
        driver.find_element(By.ID, "lg_username").send_keys(getUsername(directory, 'My Constant'))
        driver.find_element(By.ID, "lg_password").send_keys(getPassword(directory, 'My Constant'))
        driver.find_element(By.ID, "lg_password").click()
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        showMessage("CAPTCHA", "Verify captcha, then click OK")
        driver.find_element(By.XPATH, "//*[@id='submit-btn']").click()
        token = getOTP('my_constant')
        char = 0
        time.sleep(2)
        while char < 6:
            xpath_start = "//*[@id='layout']/div[3]/div/div/div[2]/div/div/div/div[3]/div/div/div["            
            driver.find_element(By.XPATH, xpath_start + str(char + 1) + "]/input").send_keys(token[char])
            char += 1
        time.sleep(6)
    except NoSuchElementException:
        exception = "caught"

def getCoinBalance(driver, coin):
        # click dropdown menu
        driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[1]/div[2]/div/div/button").click()
        # search for coin
        driver.find_element(By.ID, 'dropdown-search-selectedSymbol').send_keys(coin)
        # select coin
        driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[1]/div[2]/div/div/div/a/div/div[1]").click()
        time.sleep(6)
        return float(driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[2]/div[2]/span/span/span").text)

def getMyConstantBalances(driver, type, coinList=None):
    locateMyConstantWindow(driver)
    if (type == "USD"):
        pyautogui.moveTo(1650, 167)
        pyautogui.moveTo(1670, 167)
        pyautogui.moveTo(1650, 167)
        time.sleep(8)
        # capture and format Bonds balance
        usdBalance = Decimal(driver.find_element(By.ID, "acc_balance").text.strip('$').replace(',',''))
        return float(round(usdBalance, 2))
    elif (type == "Crypto"):
        driver.get('https://www.myconstant.com/lend-crypto-to-earn-interest')
        pyautogui.moveTo(1700, 145)
        time.sleep(2)
        # get coin balances
        for coin in coinList:
            if coin.name == "Bitcoin":
                coin.setBalance(getCoinBalance(driver, (coin.symbol)))
            elif coin.name == "Ethereum":
                coin.setBalance(getCoinBalance(driver, (coin.name)))
        return coinList


def runMyConstant(driver, type):
    locateMyConstantWindow(driver)
    Bitcoin = Crypto("Bitcoin")
    Ethereum = Crypto("Ethereum")
    balances = getMyConstantBalances(driver, type, [Bitcoin, Ethereum])
    if (type == "Crypto"):
        for coin in balances:
            account = coin.symbol + "-MyConstant"
            coin.updateSpreadsheetAndGnuCash(account)
    return balances

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(3)
    type = "Crypto"
    response = runMyConstant(driver, type)
    if (type == "USD"):
        print('myconstant balance: ' + str(response))
    elif (type == "Crypto"):
        for coin in response:
            coin.getData()
