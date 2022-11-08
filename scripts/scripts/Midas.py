import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Midas":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice, getOTP)
    from Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice, getOTP)
    from .Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl
    

def locateMidasWindow(driver):
    found = findWindowByUrl(driver, "app.midas.investments")
    if not found:
        midasLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def midasLogin(driver):
    driver.execute_script("window.open('https://app.midas.investments/?login=true&&');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
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

def getMidasBalances(driver):
    locateMidasWindow(driver)    
    driver.get("https://midas.investments/assets")
    btcBalance = float(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/ul/li[1]/div/div[3]/div[1]/span[2]").text.replace('BTC', ''))
    ethBalance = float(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/ul/li[2]/div/div[3]/div[1]/span[2]").text.replace('ETH', ''))
    return [btcBalance, ethBalance]

def runMidas(driver):
    directory = setDirectory()
    locateMidasWindow(driver)
    balances = getMidasBalances(driver)
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'BTC-Midas', 1, balances[0], "BTC")
    updateCoinQuantityFromStakingInGnuCash(balances[0], 'BTC-Midas')
    btcPrice = getCryptocurrencyPrice('bitcoin')['bitcoin']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'BTC-Midas', 2, btcPrice, "BTC")
    updateCryptoPriceInGnucash('BTC', format(btcPrice, ".2f"))

    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH-Midas', 1, balances[1], "ETH")
    updateCoinQuantityFromStakingInGnuCash(balances[1], 'ETH-Midas')
    ethPrice = getCryptocurrencyPrice('ethereum')['ethereum']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ETH-Midas', 2, ethPrice, "ETH")
    updateCryptoPriceInGnucash('ETH', format(ethPrice, ".2f"))

    return balances

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(3)
    response = runMidas(driver)
    print('btc balance: ' + str(response[0]))
    print('eth balance: ' + str(response[1]))

