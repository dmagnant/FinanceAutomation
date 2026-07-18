import time, pytesseract, re, cv2, numpy as np, random, pyautogui
from selenium.webdriver.common.keys import Keys 

if __name__ == '__main__' or __name__ == "TimeBucks":
    from Classes.Selenium import WebDriver
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, setDirectory, getLogger, putWindowInFocus, minimizeAllWindowsExcept
else:
    from .Classes.Selenium import WebDriver
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, setDirectory, getLogger, putWindowInFocus, minimizeAllWindowsExcept

def locateTimeBucksWindow(driver):
    found = driver.findWindowByUrl("timebucks.com")
    if not found:   timeBucksLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(0.5)

def timeBucksLogin(driver):
    driver.openNewWindow('https://www.timebucks.com')

def timeBucksPushClicks(driver):
    print("CODE THIS")

def timeBucksClickOffers(driver, attempts=10):
    print("CODE THIS")

def getTimeBucksBalance(driver):
    locateTimeBucksWindow(driver)
    driver.webDriver.get('https://www.timebucks.com')
    rawBalance = driver.getElementText('id', 'counter2', wait=10, allowFail=False)
    if rawBalance:  return float(rawBalance.replace('$', ''))

def runTimeBucks(driver, account, book, log=getLogger()):
    locateTimeBucksWindow(driver)
    # account.setBalance(getTimeBucksBalance(driver))
    # book.updateMRBalance(account)
    return True

if __name__ == '__main__':
    driver = WebDriver("Chrome")
    # locateTimeBucksWindow(driver)

    driver.findWindowByUrl('prime.')


        
