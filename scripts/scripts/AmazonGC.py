from selenium.webdriver.common.by import By
import time

if __name__ == '__main__' or __name__ == "AmazonGC":
    from Functions.GeneralFunctions import showMessage
    from Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance
    from Classes.WebDriver import Driver
else:
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance

def locateAmazonWindow(driver):
        found = driver.findWindowByUrl("www.amazon.com/gc/balance")
        if not found:
            driver.webDriver.execute_script("window.open('https://www.amazon.com/gc/balance');")
            driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
        else:
            driver.webDriver.switch_to.window(found)
            time.sleep(1)

def confirmAmazonGCBalance(driver):
    locateAmazonWindow(driver)
    balance = driver.webDriver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$')
    mybook = openGnuCashBook('Finance', True, True)
    amazonBalance = getGnuCashBalance(mybook, 'AmazonGC')
    if str(amazonBalance) != balance:
        showMessage("Amazon GC Mismatch", f'Amazon balance: {balance} \n' f'Gnu Cash balance: {amazonBalance} \n')
    return amazonBalance

if __name__ == '__main__':
    driver = Driver("Chrome")
    balance = confirmAmazonGCBalance(driver)
    print(balance)

