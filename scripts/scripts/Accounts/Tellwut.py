import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException, WebDriverException
import sys
sys.path.append("..")
from ..Functions import openWebDriver, showMessage

def login(driver):
    driver.execute_script("window.open('https://www.tellwut.com/signin');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        getBalance(driver)
    except NoSuchElementException:
        print('not already logged in or balance element not found')
        # click Sign In
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[4]/div/button").click()
        except NoSuchElementException:
            showMessage('Captcha or Sign in button not found', "complete captcha, then click OK. If fails, confirm element for sign in")
            driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[6]/div/button").click()
    
def getBalance(driver):
    return driver.find_element(By.XPATH, "/html/body/div/header/div/div/div/div[4]/div/div/div[2]/div[1]/div[1]").text

def completeSurveys(driver):
    if len(driver.window_handles) > 1:
        for i in driver.window_handles:
            driver.switch_to.window(i)
            if "Paid Surveys and Earn Rewards" in driver.title:
                found = True
        if not found:
            login(driver)
    else:
        if "Paid Surveys and Earn Rewards" not in driver.title:
            login(driver)
    driver.get("https://www.tellwut.com/")
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
                except ElementNotInteractableException:
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
            # re-load the webpage to load new survey
            try: 
                driver.get("https://www.tellwut.com")
            except WebDriverException:
                print('refresh error caught')
            time.sleep(2)

def redeemRewards(driver):
    balance = getBalance(driver)
    if int(balance) >= 4000:
        driver.get("https://www.tellwut.com/product/143--10-Amazon-com-e-Gift-Card.html")
        driver.find_element(By.ID, "checkout_form_submit").click()
        driver.find_element(By.ID, "form_button").click()
        driver.find_element(By.ID, "accept-additional").click()
        time.sleep(3)

def runTellwut(driver):
    login(driver)
    completeSurveys(driver)
    redeemRewards(driver)

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(3)
    runTellwut(driver)
    