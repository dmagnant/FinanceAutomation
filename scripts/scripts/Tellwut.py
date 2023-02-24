import time

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Tellwut":
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import showMessage
else:
    from .Functions.GeneralFunctions import showMessage

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
    while True:
        try:
            driver.webDriver.get('https://www.tellwut.com/most_recent_surveys') # load most recent surveys page
            time.sleep(2)
            driver.webDriver.find_element(By.XPATH,"//*[@id='surveyList']/div[1]/div[2]/div[1]/a").click() # survey link
            clickButtons(driver, 'radio')
            clickButtons(driver, 'checkbox')
            submitButton = findSubmitButton(driver)
            try:
                submitButton.click()
            except ElementClickInterceptedException:
                driver.webDriver.find_element(By.XPATH,"//*[@id='main']/section/div/div[2]/div[4]/div[1]") # scroll past to comments section
                submitButton.click()
            driver.webDriver.find_element(By.XPATH,"//*[@id='main']/div/div[2]/div[1]/div[1]/nav/ul/li[2]/a").click() # back to home page
        except NoSuchElementException:
            try:
                submitButton = findSubmitButton(driver)
                showMessage('survey not complete', 'finish survey manually')
            except NoSuchElementException:
                break

def redeemTellWutRewards(driver):
    locateTellWutWindow(driver)
    driver.webDriver.get("https://www.tellwut.com/product/143--10-Amazon-com-e-Gift-Card.html")
    driver.webDriver.find_element(By.ID, "checkout_form_submit").click()
    driver.webDriver.find_element(By.ID, "form_button").click()
    driver.webDriver.find_element(By.ID, "accept-additional").click()
    time.sleep(3)

def runTellwut(driver):
    locateTellWutWindow(driver)
    completeTellWutSurveys(driver)
    balance = getTellWutBalance(driver)
    if int(balance) >= 4000:
        redeemTellWutRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    # runTellwut(driver)
    
    found = driver.findWindowByUrl("tellwut.com/surveys")
    driver.webDriver.switch_to.window(found)
    time.sleep(1)
    type='checkbox'
    xpath = "//input[@type='" + type + "']"
    for i in driver.webDriver.find_elements(By.XPATH, xpath):
        i.click()
    # driver.webDriver.find_element(By.XPATH,'/html/body/main/section[1]/section/div/div[2]/form/div[3]/div[1]/div/div[1]/div[4]/div[1]/div[1]/input').click()
    
