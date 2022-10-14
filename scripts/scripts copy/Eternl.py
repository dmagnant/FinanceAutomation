from selenium.webdriver.common.by import By
import time

if __name__ == '__main__' or __name__ == "Eternl":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from .Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl
    

def locateEternlWindow(driver):
    found = findWindowByUrl(driver, "eternl.io/app/mainnet")
    if not found:
        eternlLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def eternlLogin(driver):
    driver.execute_script("window.open('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.implicitly_wait(10)
    
def getEternlBalance(driver):
    locateEternlWindow(driver)
    return float(driver.find_element(By.XPATH, "//*[@id='cc-main-container']/div/div[1]/div/main/div[1]/div/div[1]/div/div[1]/div[2]/div/div/div/div[1]/div").text.strip('(initializing)').replace('\n', '').strip('₳').replace(',', ''))

def runEternl(driver):
    directory = setDirectory()
    adaBalance = getEternlBalance(driver)
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ADA', 1, adaBalance, "ADA")
    updateCoinQuantityFromStakingInGnuCash(adaBalance, 'ADA')
    adaPrice = getCryptocurrencyPrice('cardano')['cardano']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ADA', 2, adaPrice, "ADA")
    updateCryptoPriceInGnucash('ADA', format(adaPrice, ".2f"))
    return adaBalance

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    response = runEternl(driver)
    print('balance: ' + str(response))
