import time
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "AmazonGC":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import showMessage
    from Functions.GnuCashFunctions import openGnuCashBook
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import openGnuCashBook

def locateAmazonWindow(driver):
        found = driver.findWindowByUrl("www.amazon.com/gc/balance")
        if not found:
            driver.openNewWindow('https://www.amazon.com/gc/balance')
        else:
            driver.webDriver.switch_to.window(found)
            time.sleep(1)

def confirmAmazonGCBalance(driver, account):
    locateAmazonWindow(driver)
    account.setBalance(driver.webDriver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$'))    
    if str(account.gnuBalance) != account.balance:
        showMessage("Amazon GC Mismatch", f'Amazon balance: {account.balance} \n' f'Gnu Cash balance: {account.gnuBalance} \n')

if __name__ == '__main__':
    readBook = openGnuCashBook('Finance', True, True)
    driver = Driver("Chrome")
    AmazonGC = USD("AmazonGC", readBook)    
    confirmAmazonGCBalance(driver, AmazonGC)
    AmazonGC.getData()
    readBook.close()
