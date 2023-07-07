import time

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Kraken":
    from Classes.Asset import Security
    from Classes.WebDriver import Driver
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
    if not found:
        krakenLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def krakenLogin(driver):
    driver.openNewWindow('https://www.kraken.com/sign-in')
    driver = driver.webDriver
    time.sleep(2)
    try:
        driver.find_element(By.ID, 'username').send_keys(getUsername('Kraken'))
        time.sleep(1)
        driver.find_element(By.ID, 'password').send_keys(getPassword('Kraken'))
        time.sleep(1)
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/form/div/div[3]/button/div/div/div").click()   
        token = getOTP('kraken_otp')
        time.sleep(1)
        driver.find_element(By.ID, 'tfa').send_keys(token)
        driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/form/div[1]/div/div/div[2]/button/div/div/div").click()
    except (NoSuchElementException or StaleElementReferenceException):
        exception = 'already logged in'
    time.sleep(2)

def getKrakenBalance(driver):
    locateKrakenWindow(driver)
    driver.webDriver.get('https://www.kraken.com/u/history/ledger')
    eth2Balance = ''
    num = 1
    while num < 20:
        balance = driver.webDriver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/span/span/span").text
        coin = driver.webDriver.find_element(By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div[3]/div[2]/div/div[" + str(num) + "]/div/div[7]/div/div/div").text
        if coin == 'ETH2':
            if not eth2Balance:
                eth2Balance = float(balance)
        num = 21 if eth2Balance else num + 1
    return eth2Balance

def runKraken(driver, account, book):
    locateKrakenWindow(driver)
    account.setBalance(getKrakenBalance(driver))
    account.setPrice(getCryptocurrencyPrice('ethereum')['ethereum']['usd'])
    account.updateBalanceInSpreadSheet()
    account.updateBalanceInGnuCash(book)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')    
    Ethereum2 = Security("Ethereum2", book)
    runKraken(driver, Ethereum2, book)
    Ethereum2.getData()
    book.closeBook()    