import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

if __name__ == '__main__' or __name__ == "Tellwut":
    from Functions.GeneralFunctions import showMessage
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import showMessage
    from .Functions.WebDriverFunctions import findWindowByUrl

def locateTellWutWindow(driver):
    found = findWindowByUrl(driver, "tellwut.com")
    if not found:
        tellwutLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def tellwutLogin(driver):
    driver.execute_script("window.open('https://www.tellwut.com/signin');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        getTellWutBalance(driver)
    except NoSuchElementException:
        print('not already logged in or balance element not found')
        # click Sign In
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[4]/div/button").click()
        except NoSuchElementException:
            showMessage('Captcha or Sign in button not found', "complete captcha, then click OK. If fails, confirm element for sign in")
            driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div[2]/div[1]/form/div[6]/div/button").click()
    driver.get("https://www.tellwut.com/")

    
def getTellWutBalance(driver):
    locateTellWutWindow(driver)
    return driver.find_element(By.XPATH, "/html/body/div/header/div/div/div/div[4]/div/div/div[2]/div[1]/div[1]").text

def completeTellWutSurveys(driver):
    locateTellWutWindow(driver)
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
    driver.get("https://www.tellwut.com/product/143--10-Amazon-com-e-Gift-Card.html")
    driver.find_element(By.ID, "checkout_form_submit").click()
    driver.find_element(By.ID, "form_button").click()
    driver.find_element(By.ID, "accept-additional").click()
    time.sleep(3)

def runTellwut(driver):
    tellwutLogin(driver)
    completeTellWutSurveys(driver)
    balance = getTellWutBalance(driver)
    if int(balance) >= 4000:
        redeemTellWutRewards(driver)

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(3)
    tellwutLogin(driver)
    