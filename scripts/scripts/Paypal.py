import csv
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Paypal":
    from Functions.GeneralFunctions import getPassword, setDirectory
    from Functions.WebDriverFunctions import openWebDriver
else:
    from .Functions.GeneralFunctions import getPassword, setDirectory

def login(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.paypal.com/us/signin');")
    time.sleep(3)
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        # enter passwordnone
        driver.find_element(By.ID, "password").send_keys(getPassword(directory, 'Paypal'))
        # click log in
        driver.find_element(By.ID,"btnLogin").click()
        time.sleep(2)
        # handle captcha
        try:
            driver.find_element(By.XPATH,"//*[@id='recaptcha-anchor']/div[1]").click()
            time.sleep(3)
            print('clicked')
        except NoSuchElementException:
            exception = "no captcha presented"
    except NoSuchElementException:
        exception = "already logged in"
        
def transferMoney(driver):
    driver.get("https://www.paypal.com/myaccount/money/")
    time.sleep(2)
    balance = driver.find_element(By.XPATH,"//*[@id='contents']/main/section/div/div/div[1]/div/p/span").text.replace('$','')
    if float(balance) > 0:
        # click transfer money
        driver.find_element(By.XPATH,"//*[@id='contents']/main/section/div/div/div[2]/a").click()
        time.sleep(2)
        # click transfer to your bank
        driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/div/div/div[1]/ul/li[1]/a/span/p[2]").click()
        time.sleep(1)
        bank = driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/form/div/div/div/div[1]/span/span[2]/span[1]").text
        if "savings" in bank.lower():
            driver.find_element(By.XPATH,"//*[@id='mainModal']/div/div/div/form/div/div/div/button").click()
    
def runPaypal(driver):
    login(driver)
    transferMoney(driver)
    
if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    response = runPaypal(driver)    
