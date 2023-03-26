import time

from selenium.common.exceptions import (NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Coinbase":
    from Classes.Asset import Crypto
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getCryptocurrencyPrice, getOTP,
                                            getPassword, getUsername)  
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import (getCryptocurrencyPrice, getOTP,
                                             getPassword, getUsername)
    
def locateCoinbaseWindow(driver):
    found = driver.findWindowByUrl("coinbase.com")
    if not found:
        coinbaseLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def coinbaseLogin(driver):
    driver.openNewWindow('https://www.coinbase.com/login')
    time.sleep(2)
    driver.webDriver.find_element(By.XPATH,"//*[@id='root']/div/div[1]/div/div/div/div/form/div[4]/ul/li/button").click() # Continue
    driver.webDriver.find_element(By.ID,"Password").send_keys(getPassword('Coinbase'))
    driver.webDriver.find_element(By.XPATH,"//*[@id='root']/div/div[1]/div/div/div/div[1]/form/div[6]/button").click() # Continue
    try:
        driver.webDriver.find_element(By.XPATH,"PATH_FOR_OTP").send_keys(getOTP('Coinbase'))
        driver.webDriver.find_element(By.XPATH,"PATH_FOR_TRUST_DEVICE").click()
    except NoSuchElementException:
        exception = "OTP not required"

def getCoinbaseBalances(driver, coinList):
    def getBasePath():
        return "//*[@id='main']/div/div/div/div/div/div/main/div[2]/div/div[1]/div/div[4]/table/tbody/tr["
    
    def getNamePath(num):
        return getBasePath() + str(num) + ']/td[1]/div/div/div[2]/div/div[1]'
                    
    def getBalancePath(num):
        return getBasePath() + str(num) + ']/td[2]/div/div/div/div/div[2]'

    locateCoinbaseWindow(driver)
    driver.webDriver.get('https://www.coinbase.com/assets')
    driver.webDriver.implicitly_wait(10)
    time.sleep(5)
    num = 1
    coinsFound = 0
    while coinsFound < len(coinList):
        name = driver.webDriver.find_element(By.XPATH, getNamePath(num)).text
        print(name)
        for coin in coinList:
            if name == coin.name:
                balance = driver.webDriver.find_element(By.XPATH, getBalancePath(num)).text.replace(' ' + coin.symbol, '').replace(',','')
                coin.setBalance(float(balance))
                coin.setPrice(getCryptocurrencyPrice(coin.name.lower())[coin.name.lower()]['usd'])
                coin.updateBalanceInSpreadSheet()
                coin.updateBalanceInGnuCash()
                coinsFound += 1
        num+=1

def runCoinbase(driver, coinList):
    locateCoinbaseWindow(driver)
    getCoinbaseBalances(driver, coinList)
    
if __name__ == '__main__':
    # driver = Driver("Chrome")
    # Loopring = Crypto("Loopring")
    # runCoinbase(driver, [Loopring])
    # Loopring.getData()
    color = 'blue'
    
    Test = {
        'test': color
    }
    print(Test['test'])
    
    Test['test'] = 'red'
    
    print(Test['test'])
