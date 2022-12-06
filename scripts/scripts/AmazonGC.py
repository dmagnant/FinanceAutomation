from selenium.webdriver.common.by import By
import time

if __name__ == '__main__' or __name__ == "AmazonGC":
    from Functions.GeneralFunctions import showMessage
    from Classes.WebDriver import Driver
    from Classes.Asset import USD
else:
    from .Functions.GeneralFunctions import showMessage
    from .Classes.Asset import USD

def locateAmazonWindow(driver):
        found = driver.findWindowByUrl("www.amazon.com/gc/balance")
        if not found:
            driver.webDriver.execute_script("window.open('https://www.amazon.com/gc/balance');")
            driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
        else:
            driver.webDriver.switch_to.window(found)
            time.sleep(1)

def confirmAmazonGCBalance(driver):
    AmazonGC = USD("AmazonGC")
    locateAmazonWindow(driver)
    AmazonGC.setBalance(driver.webDriver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$'))    
    if str(AmazonGC.gnuBalance) != AmazonGC.balance:
        showMessage("Amazon GC Mismatch", f'Amazon balance: {AmazonGC.balance} \n' f'Gnu Cash balance: {AmazonGC.gnuBalance} \n')
    return AmazonGC

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = confirmAmazonGCBalance(driver)
    response.getData()

