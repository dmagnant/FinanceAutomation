import time

from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Eternl":
    from Classes.Asset import Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash

def locateEternlWindow(driver):
    found = driver.findWindowByUrl("eternl.io/app/mainnet")
    if not found:
        eternlLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def eternlLogin(driver):
    driver.openNewWindow('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary')
    time.sleep(1)
    
def getEternlBalance(driver):
    locateEternlWindow(driver)
    return float(driver.webDriver.find_element(By.XPATH, "//*[@id='cc-main-container']/div/div[1]/div/main/div[1]/div/div[1]/div/div[1]/div[2]/div/div/div/div[1]/div").text.strip('(initializing)').replace('\n', '').strip('₳').replace(',', ''))

def runEternl(driver, account, book):
    account.setBalance(getEternlBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)
    

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Cardano = Security("Cardano", book , 'ADA-Eternl')    
    runEternl(driver, Cardano, book)
    Cardano.getData()
    book.closeBook()
    