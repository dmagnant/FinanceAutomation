from selenium.webdriver.common.by import By
import time

if __name__ == '__main__' or __name__ == "Eternl":
    from Classes.Asset import Crypto
    from Classes.WebDriver import Driver
else:
    from .Classes.Asset import Crypto

def locateEternlWindow(driver):
    found = driver.findWindowByUrl("eternl.io/app/mainnet")
    if not found:
        eternlLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def eternlLogin(driver):
    driver.execute_script("window.open('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)
    driver.implicitly_wait(10)
    
def getEternlBalance(driver):
    locateEternlWindow(driver)
    return float(driver.webDriver.find_element(By.XPATH, "//*[@id='cc-main-container']/div/div[1]/div/main/div[1]/div/div[1]/div/div[1]/div[2]/div/div/div/div[1]/div").text.strip('(initializing)').replace('\n', '').strip('₳').replace(',', ''))

def runEternl(driver):
    Cardano = Crypto("Cardano")
    Cardano.setBalance(getEternlBalance(driver))
    Cardano.setPrice(Cardano.getPriceFromCoinGecko())
    Cardano.updateSpreadsheetAndGnuCash()
    return [Cardano]

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runEternl(driver)
    for coin in response:
        coin.getData()
