import time

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Tellwut":
    from Classes.WebDriver import Driver
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage
    from Functions.GnuCashFunctions import openGnuCashBook
else:
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import openGnuCashBook   
    from .Classes.Asset import Crypto

def locateTellWutWindow(driver):
    found = driver.findWindowByUrl("tellwut.com")
    if not found:
        tellwutLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def tellwutLogin(driver):
    driver.openNewWindow('https://www.tellwut.com/')
    try:
        driver.webDriver.find_element(By.XPATH,'/html/body/main/header/button[2]').click() # LOGIN button
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH,"//*[@id='loginForm']/button").click() # LOGIN button (again)
    except NoSuchElementException:
        exception = 'already logged in'
        
def getTellWutBalance(driver):
    locateTellWutWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/main/header/a[2]/div/div[2]/span").text

def clickButtons(driver, type):
    xpath = "//input[@type='" + type + "']"
    for i in driver.webDriver.find_elements(By.XPATH, xpath): # click all checkboxes
        try:
            i.click()
        except(ElementNotInteractableException):
            exception = 'notInteractable'
        except(ElementClickInterceptedException):
            if type == 'radio':
                findSubmitButton(driver)
                i.click()

def findSubmitButton(driver):
    return driver.webDriver.find_element(By.ID,'survey_form_submit')

def completeTellWutSurveys(driver):
    locateTellWutWindow(driver)
    driver.webDriver.implicitly_wait(2)
    driver.webDriver.get('https://www.tellwut.com/most_recent_surveys') # load most recent surveys page
    time.sleep(2)
    try:
        driver.webDriver.find_element(By.XPATH,"//*[@id='surveyList']/div[1]/div[2]/div[1]/a").click() # survey link
    except NoSuchElementException:
        exception = "no surveys"
        return False
    while True:
        try:
            clickButtons(driver, 'radio')
            clickButtons(driver, 'checkbox')
            submitButton = findSubmitButton(driver)
            try:
                submitButton.click()
            except ElementClickInterceptedException:
                driver.webDriver.find_element(By.XPATH,"//*[@id='main']/section/div/div[2]/div[4]/div[1]") # scroll past to comments section
                submitButton.click()
            time.sleep(8)
            driver.webDriver.find_element(By.XPATH,"//*[@id='next-survey-btn']/a").click() # NEXT POLL
        except NoSuchElementException:
            try:
                submitButton = findSubmitButton(driver)
                showMessage('survey not complete', 'finish survey manually')
                driver.webDriver.find_element(By.XPATH,"//*[@id='next-survey-btn']/a").click() # NEXT POLL
            except NoSuchElementException:
                break

def redeemTellWutRewards(driver):
    locateTellWutWindow(driver)
    driver.webDriver.get("https://www.tellwut.com/product/143--10-Amazon-com-e-Gift-Card.html")
    driver.webDriver.find_element(By.ID, "checkout_form_submit").click()
    driver.webDriver.find_element(By.ID, "form_button").click()
    driver.webDriver.find_element(By.ID, "accept-additional").click()
    time.sleep(3)

def runTellwut(driver, account, book):
    locateTellWutWindow(driver)
    completeTellWutSurveys(driver)
    account.setBalance(getTellWutBalance(driver))
    account.updateMRBalance(book)
    if int(account.balance) >= 4000:
        redeemTellWutRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = openGnuCashBook('Finance', False, False)
    Tellwut = Crypto("Tellwut", book)
    runTellwut(driver, Tellwut, book)
    Tellwut.getData()
    if not book.is_saved:
        book.save()
    book.close()
    