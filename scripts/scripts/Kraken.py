import time

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Kraken":
    from Functions.GeneralFunctions import (setDirectory, getCryptocurrencyPrice, getOTP, getUsername, getPassword)
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
    from Classes.Asset import Crypto    
else:
    from .Functions.GeneralFunctions import (setDirectory, getCryptocurrencyPrice, getOTP, getUsername, getPassword)
    from .Functions.WebDriverFunctions import findWindowByUrl
    from .Classes.Asset import Crypto
    
def locateKrakenWindow(driver):
    found = findWindowByUrl(driver, "kraken.com")
    if not found:
        krakenLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def krakenLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.kraken.com/sign-in');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(2)
    try:
        driver.find_element(By.ID, 'username').send_keys(getUsername(directory, 'Kraken'))
        time.sleep(1)
        driver.find_element(By.ID, 'password').send_keys(getPassword(directory, 'Kraken'))
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/form/div/div[3]/button/div/div/div").click()   
        token = getOTP('kraken_otp')
        time.sleep(1)
        driver.find_element(By.ID, 'tfa').send_keys(token)
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/form/div[1]/div/div/div[2]/button/div/div/div").click()
    except (NoSuchElementException, StaleElementReferenceException):
        exception = 'already logged in'
    time.sleep(2)

def getKrakenBalances(driver):
    locateKrakenWindow(driver)
    driver.get('https://www.kraken.com/u/history/ledger')
    eth2Balance = ''
    num = 1
    while num < 20:
        balance = driver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/span/span/span").text
        coin = driver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/div").text
        if coin == 'ETH2':
            if not eth2Balance:
                eth2Balance = float(balance)
        num = 21 if eth2Balance else num + 1
    return [eth2Balance]

def runKraken(driver):
    locateKrakenWindow(driver)
    Ethereum2 = Crypto("Ethereum2")
    balances = getKrakenBalances(driver)
    coinList = [Ethereum2]
    for coin in coinList:
        if coin.name == "Ethereum2":
            Ethereum2.setBalance(balances[0])
            Ethereum2.setPrice(getCryptocurrencyPrice('ethereum')['ethereum']['usd'])
            Ethereum2.updateBalanceInSpreadSheet()
            Ethereum2.updateBalanceInGnuCash()
    return coinList

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(2)
    response = runKraken(driver)
    for coin in response:
        coin.getData()
        