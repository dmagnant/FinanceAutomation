import os
import time

import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Bing":
    from Classes.Asset import Crypto
    from Classes.WebDriver import Driver
    from Functions.GnuCashFunctions import openGnuCashBook
else:
    from .Classes.Asset import Crypto 
    from .Classes.WebDriver import Driver
    from .Functions.GnuCashFunctions import openGnuCashBook
 
def locateBingWindow(driver):
    found = driver.findWindowByUrl("rewards.bing.com")
    if not found:
        bingLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
    return True
   
def bingLogin(driver):
    driver.openNewWindow('https://rewards.bing.com')
    time.sleep(2)
    driver.webDriver.implicitly_wait(1)
    time.sleep(1)
    try:
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/section/div[1]/div[2]/section/div[1]/a[2]").click() # sign in
        time.sleep(1)
        driver.webDriver.find_element(By.ID, "idSIButton9").click() # next
        time.sleep(1)
        time.sleep(1)
        driver.webDriver.find_element(By.ID, "idSIButton9").click() # sign in
        time.sleep(1)
        driver.webDriver.find_element(By.XPATH, "/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input").click() # stay signed in
        driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/section/div[1]/div[2]/section/div[1]/a[2]").click() # sign in link
    except NoSuchElementException:
        exception = "already logged in"

def bingActivities(driver):
    locateBingWindow(driver)
    pointsLinks = driver.webDriver.find_elements(By.CSS_SELECTOR, "div.actionLink.x-hidden-vp1")
    pointsLinks[0].click() # first link
    time.sleep(1)
    driver.switchToLastWindow()
    time.sleep(1)
    driver.webDriver.close()
    driver.switchToLastWindow()
    pointsLinks[2].click() # Daily Poll
    time.sleep(1)
    driver.switchToLastWindow()
    try:
        if driver.webDriver.find_element(By.XPATH, '/html/body/div[2]/div[2]/span/a'):
            time.sleep(1)
            driver.webDriver.close()
            driver.switchToLastWindow()
            time.sleep(1)
            pointsLinks[2].click()
            driver.switchToLastWindow()
    except NoSuchElementException:
        exception = "caught"
    time.sleep(2)
    pyautogui.leftClick(350, 950)
    time.sleep(2)
    pyautogui.leftClick(1225, 925) # multiple choice option
    pyautogui.leftClick(350, 950) # click True
    time.sleep(1)
    pyautogui.leftClick(425, 950) # click False
    driver.webDriver.close()
    driver.switchToLastWindow()

def getBingBalance(driver):
    locateBingWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='balanceToolTipDiv']/p/mee-rewards-counter-animation/span").text.replace(',', '')

def claimBingRewards(driver):
    locateBingWindow(driver)
    driver.webDriver.get("https://rewards.microsoft.com/redeem/000800000000")     # go to $5 Amazon gift card link
    time.sleep(3)
    driver.webDriver.find_element(By.XPATH, "//*[@id='redeem-pdp_000800000000']/span[1]").click() # Redeem Reward
    time.sleep(3)
    driver.webDriver.find_element(By.XPATH, "//*[@id='redeem-checkout-review-confirm']/span[1]").click() # Confirm Reward
    try:
        driver.webDriver.find_element(By.ID, "redeem-checkout-challenge-fullnumber").send_keys(os.environ.get('Phone'))
        driver.webDriver.find_element(By.XPATH, "//*[@id='redeem-checkout-challenge-validate']/span").click() # Send
    except NoSuchElementException:
        exception = "caught"

def runBing(driver, account, book):
    locateBingWindow(driver)
    bingActivities(driver)
    account.setBalance(getBingBalance(driver))
    account.updateMRBalance(book)
    if int(account.balance) >= 5250:
        claimBingRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = openGnuCashBook('Finance', False, False)
    Bing = Crypto("Bing", book)
    runBing(driver, Bing, book)
    Bing.getData()
    if not book.is_saved:
        book.save()
    book.close()
    