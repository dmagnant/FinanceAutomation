import time
from decimal import Decimal

import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from Functions.Functions import (openWebDriver, getCryptocurrencyPrice, getOTP,
                       getPassword, getUsername, setDirectory, showMessage,
                       updateCoinQuantityFromStakingInGnuCash,
                       updateCryptoPriceInGnucash, updateSpreadsheet)


def login(directory, driver):
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
            xpath_start = "//*[@id='layout']/div[2]/div/div/div[2]/div/div/div/div[3]/div/div/div["
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
        return driver.find_element(By.XPATH, "//*[@id='layout']/div[2]/div/div/div/div[2]/div[2]/form/div[2]/div[2]/span/span/span").text

def captureBalances(driver, type):
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
        btcBalance = getCoinBalance(driver, ('BTC'))
        ethBalance = getCoinBalance(driver, ('ETHEREUM'))
        return [btcBalance, ethBalance]


def runMyConstant(directory, driver, type):
    login(directory, driver)
    balances = captureBalances(driver, type)
    if (type == "Crypto"):
        # BTC
        updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'BTC-MyConstant', 1, balances[0], "BTC")
        updateCoinQuantityFromStakingInGnuCash(balances[0], 'BTC-MyConstant')
        btcPrice = getCryptocurrencyPrice('bitcoin')['bitcoin']['usd']
        updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'BTC-MyConstant', 2, btcPrice, "BTC")
        updateCryptoPriceInGnucash('BTC', format(btcPrice, ".2f"))
        # ETH
        updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH-MyConstant', 1, balances[1], "ETH")
        updateCoinQuantityFromStakingInGnuCash(balances[1], 'ETH-MyConstant')
        ethPrice = getCryptocurrencyPrice('ethereum')['ethereum']['usd']
        updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH-MyConstant', 2, ethPrice, "ETH")
        updateCryptoPriceInGnucash('ETH', format(ethPrice, ".2f"))
    return balances

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(3)
    type = "Crypto"
    response = runMyConstant(directory, driver, type)
    if (type == "USD"):
        print('myconstant balance: ' + str(response))
    elif (type == "Crypto"):
        print('btc balance: ' + str(response[0]))
        print('eth balance: ' + str(response[1]))
