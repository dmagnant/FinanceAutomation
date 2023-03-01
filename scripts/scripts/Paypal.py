import time
import pyautogui

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Paypal":
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import getPassword
else:
    from .Functions.GeneralFunctions import getPassword

def locatePayPalWindow(driver):
    found = driver.findWindowByUrl("paypal.com/myaccount")
    if not found:
        response = payPalLogin(driver)
        if response:
            print('response here')
            return "notLoggedIn"
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def payPalLogin(driver):
    driver.openNewWindow('https://www.paypal.com/us/signin')
    driver = driver.webDriver
    time.sleep(3)
    num = 1
    while num <3:
        try:
            # enter password
            # driver.find_element(By.ID, "password").send_keys(getPassword('Paypal'))
            # click log in
            driver.find_element(By.ID,"btnLogin").click()
            time.sleep(2)
            # handle captcha
            try:
                driver.find_element(By.XPATH,"//*[@id='content']/h1")
                pyautogui.moveTo(825,400)
                pyautogui.leftClick(825,400)
                time.sleep(5)
            except (NoSuchElementException):
                exception = "no captcha presented"
        except NoSuchElementException:
            exception = "already logged in"
        try:
            driver.find_element(By.ID, "password")
        except NoSuchElementException:
            break
        num+=1

def transferMoney(driver):
    balance = driver.find_element(By.XPATH,"//*[@id='cwBalance']/div/div/div[1]").text.replace('$','')
    print(balance)
    if float(balance) > 0:
        # click transfer money
        driver.find_element(By.XPATH,"//*[@id='cwBalance']/div/div/a").click()
        time.sleep(2)
        # click transfer to your bank
        driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/div/div/div[1]/ul/li[1]/a/span/p[2]").click()
        time.sleep(1)
        bank = driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/form/div/div/div/div[1]/span/span[2]/span[1]").text
        if "savings" in bank.lower():
            driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/form/div/div/div/button").click()
        
def runPaypal(driver):
    response = locatePayPalWindow(driver)
    if response != "notLoggedIn":
        transferMoney(driver.webDriver)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    runPaypal(driver)
