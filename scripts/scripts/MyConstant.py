import time, pyautogui
from decimal import Decimal
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "MyConstant":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getOTP, getPassword, getUsername, showMessage)
else:
    from .Classes.Asset import USD, Security
    from .Functions.GeneralFunctions import (getOTP, getPassword, getUsername, showMessage)

def locateMyConstantWindow(driver):
    found = driver.findWindowByUrl("www.myconstant.com")
    if not found:   myConstantLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def myConstantLogin(driver):
    driver.openNewWindow('https://www.myconstant.com/log-in')
    driver = driver.webDriver
    try:
        driver.find_element(By.ID, "lg_username").send_keys(getUsername('My Constant'))
        driver.find_element(By.ID, "lg_password").send_keys(getPassword('My Constant'))
        driver.find_element(By.ID, "lg_password").click()
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('space')
        showMessage("CAPTCHA", "Verify captcha, then click OK")
        driver.find_element(By.XPATH, "//*[@id='submit-btn']").click()
        token, char = getOTP('my_constant'), 0
        time.sleep(2)
        while char < 6:
            xpath_start = "//*[@id='layout']/div[3]/div/div/div[2]/div/div/div/div[3]/div/div/div["            
            driver.find_element(By.XPATH, xpath_start + str(char + 1) + "]/input").send_keys(token[char])
            char += 1
        time.sleep(6)
    except NoSuchElementException:  exception = "caught"

def getCoinBalance(driver, coin):
        # click dropdown menu
        driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[1]/div[2]/div/div/button").click()
        # search for coin
        driver.find_element(By.ID, 'dropdown-search-selectedSymbol').send_keys(coin)
        # select coin
        driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[1]/div[2]/div/div/div/a/div/div[1]").click()
        time.sleep(6)
        return float(driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[2]/div[2]/span/span/span").text)

def getMyConstantBalances(driver, type):
    locateMyConstantWindow(driver)
    MyConstant = USD("MyConstant")
    if (type == "USD"):
        pyautogui.moveTo(1650, 167)
        pyautogui.moveTo(1670, 167)
        pyautogui.moveTo(1650, 167)
        time.sleep(8)
        # capture and format Bonds balance
        usdBalance = float(round(Decimal(driver.webDriver.find_element(By.ID, "acc_balance").text.strip('$').replace(',','')), 2))
        MyConstant.setBalance(usdBalance)
        return MyConstant
    elif (type == "Crypto"):
        driver.webDriver.get('https://www.myconstant.com/lend-crypto-to-earn-interest')
        pyautogui.moveTo(1700, 145)
        time.sleep(2)
        Bitcoin = Security("Bitcoin")
        Ethereum = Security("Ethereum")
        coinList = [Bitcoin, Ethereum]
        for coin in coinList:
            if coin.name == "Bitcoin":      coin.setBalance(getCoinBalance(driver, (coin.symbol)))
            elif coin.name == "Ethereum":   coin.setBalance(getCoinBalance(driver, (coin.name)))
        return coinList

def runMyConstant(driver, type):
    locateMyConstantWindow(driver)
    balances = getMyConstantBalances(driver, type)
    if (type == "Crypto"):
        for coin in balances:
            account = coin.symbol + "-MyConstant"
            coin.updateSpreadsheetAndGnuCash(account)
    return balances

if __name__ == '__main__':
    driver = Driver("Chrome")
    type = "USD"
    response = runMyConstant(driver, type)
    if (type == "USD"): response.getData()
    elif (type == "Crypto"):
        for coin in response:   coin.getData()
