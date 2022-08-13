from selenium.webdriver.common.by import By

from Functions.Functions import (openWebDriver, getCryptocurrencyPrice,
                       setDirectory, updateCoinQuantityFromStakingInGnuCash,
                       updateCryptoPriceInGnucash, updateSpreadsheet)


def runEternl(directory, driver):
    driver.execute_script("window.open('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary');")

    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.implicitly_wait(10)
    adaBalance = float(driver.find_element(By.XPATH, "//*[@id='cc-main-container']/div/div[3]/div[2]/nav/div/div[2]/div/div/div/div[3]").text.strip('(initializing)').replace('\n', '').strip('₳').replace(',', ''))
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ADA', 1, adaBalance, "ADA")
    updateCoinQuantityFromStakingInGnuCash(adaBalance, 'ADA')
    adaPrice = getCryptocurrencyPrice('cardano')['cardano']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ADA', 2, adaPrice, "ADA")
    updateCryptoPriceInGnucash('ADA', format(adaPrice, ".2f"))
    return adaBalance

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    response = runEternl(directory, driver)
    print('balance: ' + str(response))
