import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "HealthEquity":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage, setDirectory, getPassword, getAnswerForSecurityQuestion)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage, setDirectory, getPassword, getAnswerForSecurityQuestion)  
    
def locateOptumWindow(driver):
    found = driver.findWindowByUrl("secure.optumfinancial.com")
    if not found:   optumLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    
def answerOptumSecurityQuestions(driver):
    try:
        question = driver.webDriver.find_element(By.XPATH, "//*[@id='answer-0_container']/div[1]/label/span").text
        print(question)
        driver.webDriver.find_element(By.ID, 'answer-0').send_keys(getAnswerForSecurityQuestion(question))
        driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/main/div[3]/div/div[2]/form/div/div[2]/div").click() # Trust this device
        driver.webDriver.find_element(By.ID, 'submitBtn').click() # Continue
    except NoSuchElementException:  exception = 'no security questions'
        
def optumLogin(driver):
    driver.openNewWindow('https://secure.optumfinancial.com/portal/hsid/login?url=/portal/CC')
    try:
        driver.webDriver.find_element(By.ID, "password").send_keys(getPassword('Optum HSA'))
        driver.webDriver.find_element(By.ID, "submitBtn").click() # Sign in
        time.sleep(3)
        answerOptumSecurityQuestions(driver)
    except StaleElementReferenceException:
        answerOptumSecurityQuestions(driver)
    except NoSuchElementException:      exception = "already logged in"
    time.sleep(1)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    VFIAX = Security("Optum Investment", book)
    OptumCash = USD("Optum Cash", book)
    OptumAccounts = {'VFIAX': VFIAX, 'OptumCash': OptumCash}
    locateOptumWindow(driver)
    