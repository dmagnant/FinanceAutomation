import time

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Kraken":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice, getOTP, getUsername, getPassword)
    from Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice, getOTP, getUsername, getPassword)
    from .Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl
    
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
    dotBalance = ''
    eth2Balance = ''
    num = 1
    while num < 20:
        balance = driver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/span/span/span").text
        coin = driver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/div").text
        if coin == 'DOT':
            if not dotBalance:
                dotBalance = float(balance)
        elif coin == 'ETH2':
            if not eth2Balance:
                eth2Balance = float(balance)
        num = 21 if eth2Balance and dotBalance else num + 1
    
    return [dotBalance, eth2Balance]

def runKraken(driver):
    directory = setDirectory()
    locateKrakenWindow(driver)
    balances = getKrakenBalances(driver)
    
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'DOT', 1, balances[0], "DOT")
    updateCoinQuantityFromStakingInGnuCash(balances[0], 'DOT')
    dotPrice = getCryptocurrencyPrice('polkadot')['polkadot']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'DOT', 2, dotPrice, "DOT")
    updateCryptoPriceInGnucash('DOT', format(dotPrice, ".2f"))

    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH2', 1, balances[1], "ETH2")
    updateCoinQuantityFromStakingInGnuCash(balances[1], 'ETH2')
    eth2Price = getCryptocurrencyPrice('ethereum')['ethereum']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH-Kraken', 2, eth2Price, "ETH")
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH2', 2, eth2Price, "ETH2")
    updateCryptoPriceInGnucash('ETH', format(eth2Price, ".2f"))
    updateCryptoPriceInGnucash('ETH2', format(eth2Price, ".2f"))

    return balances

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(2)
    response = runKraken(directory, driver)
    print('dot balance: ' + str(response[0]))
    print('eth2 balance: ' + str(response[1]))
