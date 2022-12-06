import time

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

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
    driver.webDriver.execute_script("window.open('https://www.tellwut.com/signin');")
    driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
    try:
        getTellWutBalance(driver)
    except NoSuchElementException:
        print('not already logged in or balance element not found')
        # click Sign In
        try:
            driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[4]/div/button").click()
        except NoSuchElementException:
            showMessage('Captcha or Sign in button not found', "complete captcha, then click OK. If fails, confirm element for sign in")
            driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[6]/div/button").click()
    driver.webDriver.get("https://www.tellwut.com/")

def getTellWutBalance(driver):
    locateTellWutWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/header/div/div/div/div[4]/div/div/div[2]/div[1]/div[1]").text

def completeTellWutSurveys(driver):
    locateTellWutWindow(driver)
    driver = driver.webDriver
    driver.implicitly_wait(2)
    while True:
            try:
                # look for "Start Survey" button
                driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[2]/div[1]/form/div[1]/div/button").click()
            except ElementClickInterceptedException:
                # click randomize
                driver.find_element(By.XPATH, "/html/body/div/main/div[2]/div[2]/div[1]/div/h1/a").click()
                print('randomize clicked')
            except NoSuchElementException:
                try:
                    # look for submit button
                    driver.find_element(By.XPATH, "//input[@id='survey_form_submit']")
                    # if no submit button, stop
                except NoSuchElementException:
                    break
            # click on all radio buttons
            for i in driver.find_elements(By.XPATH, "//input[@type='radio']"):
                try:
                    i.click()
                except (ElementNotInteractableException, ElementClickInterceptedException):
                    exception = "caught"
            # click on all checkboxes
            for i in driver.find_elements(By.XPATH,"//input[@type='checkbox']"):
                try:
                    i.click()
                except (ElementNotInteractableException, ElementClickInterceptedException):
                    exception = "caught"
            # Click Submit
            driver.find_element(By.XPATH, "//input[@id='survey_form_submit']").click()
            time.sleep(3)
            driver.get("https://www.tellwut.com")
            time.sleep(2)

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
    runTellwut(driver)
    