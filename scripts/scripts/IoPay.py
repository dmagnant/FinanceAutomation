import time
from decimal import Decimal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import math

if __name__ == '__main__' or __name__ == "IoPay":
    from Classes.Asset import Security
    from Functions.GeneralFunctions import showMessage
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage

def locateIoPayWindow(driver):
    found = driver.findWindowByUrl("stake.iotex.io")
    if not found:
        IoPayLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def IoPayLogin(driver):
    driver.openNewWindow('https://stake.iotex.io/')
    time.sleep(1)

def runIoPay(driver, account, book):
    locateIoPayWindow(driver)
    showMessage('Open Ledger Wallet - IoPay App', 'Once Open, click OK')
    driver.webDriver.implicitly_wait(10)
    try:
        driver.webDriver.find_element(By.XPATH,"//*[@id='__next']/section/nav/div/div[2]/div/div/button[1]").click() # connect wallet
        driver.webDriver.find_element(By.XPATH,"//*[@id='chakra-modal--body-1']/div/div[2]").click() # ledger
        driver.webDriver.find_element(By.XPATH,"//*[@id='chakra-modal--body-2']/div[1]/div/div[2]/button").click() # Connect
    except NoSuchElementException:
        exception = "wallet already connected"
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH,"//*[@id='__next']/section/nav/div/div[2]/nav/div[4]/div/div/p").click() # click my Vote
    time.sleep(1)
    walletBalance = Decimal(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/section/div[1]/main/div/div[5]/div[2]/div[2]/div[3]/div[3]/div[2]/div[2]/p[2]").text.replace(" IOTX", ""))
    if walletBalance > 5:
        driver.webDriver.find_element(By.XPATH,'/html/body/div[1]/section/div[1]/main/div/div[5]/div[2]/div[2]/div[3]/div[3]/div[1]/div/div/div[2]/div[1]/div/div[2]/div[6]/div/button').click() # action
        driver.webDriver.find_element(By.XPATH,'/html/body/div[5]/div/div/button[2]/div[1]').click() # add stake
        driver.webDriver.find_element(By.XPATH,'/html/body/div[5]/div[2]/div[4]/div/section/div/div/div[1]/div/div[1]/div/div[1]/input').send_keys(str(math.floor(walletBalance))) # wallet balance
        driver.webDriver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[4]/div/section/footer/button[2]').click() # OK
        showMessage('Approve transaction on Ledger', 'Once complete, click OK')
        
    walletBalance = Decimal(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/section/div[1]/main/div/div[5]/div[2]/div[2]/div[3]/div[3]/div[2]/div[2]/p[2]").text.replace(" IOTX", ""))
    stakedBalance = Decimal(driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/section/div[1]/main/div/div[5]/div[2]/div[2]/div[3]/div[3]/div[2]/div[3]/p[2]").text.replace(" IOTX", "").replace(',',''))
    iotxBalance = round(float(walletBalance + stakedBalance), 2)
    account.setBalance(iotxBalance)
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)

if __name__ == '__main__':                                                                  
    driver = Driver("Chrome")
    book = GnuCash('Finance')    
    IoTex = Security("IoTex", book)
    runIoPay(driver, IoTex, book)
    IoTex.getData()
    book.closeBook()
    