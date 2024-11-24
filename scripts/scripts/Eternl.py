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
    if not found:   eternlLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def eternlLogin(driver):
    driver.openNewWindow('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary')
    time.sleep(1)
    
def getEternlBalance(driver):
    locateEternlWindow(driver)
    while True:
        status = driver.getXPATHElementTextOnceAvailable("//*[@id='cc-main-container']/div/div[3]/div[2]/nav/div/div[2]/div/div/div[1]/div[2]/div/span").replace('\n', '')
        if 'initializing' in status or 'Syncing' in status:
            time.sleep(2)
            driver.webDriver.refresh()
            time.sleep(2)
        else:                           break
    balance = float(driver.webDriver.find_element(By.XPATH,"//*[@id='cc-main-container']/div/div[3]/div[2]/nav/div/div[2]/div/div/div[1]/div[2]/div/div").text.replace('\n', '').replace('₳','').replace(',', ''))
    return balance + float(2580) # balance current in Coinbase

def runEternl(driver, account, book):
    account.setBalance(getEternlBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Cardano = Security("Cardano", book)    
    runEternl(driver, Cardano, book)
    Cardano.getData()
    book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateEternlWindow(driver)
                                         
    driver.webDriver.refresh()