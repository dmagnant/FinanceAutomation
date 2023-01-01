import time
from decimal import Decimal
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "IoPay":
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage
    from Classes.WebDriver import Driver
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage    

def locateIoPayWindow(driver):
    found = driver.findWindowByUrl("stake.iotex.io")
    if not found:
        IoPayLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def IoPayLogin(driver):
    driver.execute_script("window.open('https://stake.iotex.io/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)

def runIoPay(driver):
    IoTex = Crypto("IoTex")
    locateIoPayWindow(driver)
    showMessage('Open Ledger Wallet - IoPay App', 'Once Open, click OK')
    # click Connect Wallet
    driver.webDriver.find_element(By.XPATH,"//*[@id='__next']/section/nav/div/div[2]/div/div/button[1]").click()
    # click Ledger
    driver.webDriver.find_element(By.XPATH,"//*[@id='chakra-modal--body-1']/div/div[3]").click()
    time.sleep(2)
    driver.webDriver.find_element(By.XPATH,"//*[@id='__next']/section/nav/div/div[2]/nav/div[4]/div/div/p").click()
    walletBalance = Decimal(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/section/div[1]/main/div/div[4]/div[2]/div[2]/div[3]/div[3]/div[2]/div[2]/p[2]").text.replace(" IOTX", ""))
    stakedBalance = Decimal(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/section/div[1]/main/div/div[4]/div[2]/div[2]/div[3]/div[3]/div[2]/div[3]/p[2]").text.replace(" IOTX", "").replace(',',''))
    iotxBalance = round(float(walletBalance + stakedBalance), 2)
    IoTex.setBalance(iotxBalance)
    IoTex.setPrice(IoTex.getPriceFromCoinGecko())
    IoTex.updateSpreadsheetAndGnuCash()
    return IoTex

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runIoPay(driver)
    response.getData()

