import time

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Kraken":
    from Classes.Asset import Security
    from Classes.Selenium import WebDriver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getCryptocurrencyPrice, getOTP,
                                            getPassword, getUsername)
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getCryptocurrencyPrice, getOTP,
                                             getPassword, getUsername)
    
def locateKrakenWindow(driver):
    found = driver.findWindowByUrl("kraken.com")
    if not found:   krakenLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def krakenLogin(driver):
    driver.openNewWindow('https://id.kraken.com/sign-in')
    driver.randomSleep(3,5)
    # driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="username"]', getUsername('Kraken'))
    # driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="password"]', getPassword('Kraken'))
    driver.getElementAndClick('xpath', '//span[contains(text(), "Continue")]')
    driver.randomSleep(4,7)
    driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="tfa"]', getOTP('kraken_otp'))
    driver.randomSleep(1,3)
    element = driver.getVisibleElement('xpath', '//span[contains(text(), "Enter")]', locate=False)
    driver.clickElement(element)

def getKrakenBalance(driver):
    locateKrakenWindow(driver)
    driver.webDriver.get('https://www.kraken.com/u/history/ledger')
    eth2Balance, num = '', 1
    while num < 20:
        balance = driver.webDriver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/span/span/span").text
        coin = driver.webDriver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/div").text
        if coin == 'ETH2':
            if not eth2Balance: eth2Balance = float(balance)
        num = 21 if eth2Balance else num + 1
    return eth2Balance

def runKraken(driver, account, book):
    locateKrakenWindow(driver)
    account.setBalance(getKrakenBalance(driver))
    account.setPrice(getCryptocurrencyPrice('ethereum')['ethereum']['usd'])
    account.updateBalanceInSpreadSheet()
    account.updateBalanceInGnuCash(book)

if __name__ == '__main__':
    driver = WebDriver("Chrome")
    # locateKrakenWindow(driver)
    # book = GnuCash('Finance')    
    # Ethereum2 = Security("Ethereum2", book)
    # runKraken(driver, Ethereum2, book)
    # Ethereum2.getData()
    # book.closeBook()    

    driver.findWindowByUrl("kraken.com")
    # ele = driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="username"]', getUsername('Kraken'))
    # ele = driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="password"]', getPassword('Kraken'))
    # driver.getElementAndClick('xpath', '//span[contains(text(), "Continue")]')
    ele = driver.getElementAndSendKeys('CSS_SELECTOR', 'input[name="tfa"]', getOTP('kraken_otp'))
    element = driver.getVisibleElement('xpath', '//span[contains(text(), "Enter")]', locate=False)
    driver.clickElement(element, path='test')