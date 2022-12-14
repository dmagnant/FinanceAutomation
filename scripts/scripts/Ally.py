import csv
import time
from datetime import datetime
from decimal import Decimal
import re

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                             getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription

def locateAllyWindow(driver):
    found = driver.findWindowByUrl("secure.ally.com")
    if not found:
        allyLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def allyLogin(driver):
    directory = setDirectory()
    # closeExpressVPN()
    driver.implicitly_wait(10)
    loggedIn = False
    while not loggedIn:
        driver.execute_script("window.open('https://ally.com/');")
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        time.sleep(1)
        # click Login
        driver.find_element(By.ID,"login").click()
        # enter Password (username already filled in)
        driver.find_element(By.ID,"allysf-login-v2-password-367761b575af35f6ccb5b53e96b2fa2d").send_keys(getPassword(directory, 'Ally Bank'))
        # click Login
        driver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button").click()
        time.sleep(5)
        # check if login button is still seen
        try:
            driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[1]/form/div[3]/button/span")
            loggedIn = False
        except NoSuchElementException:
            loggedIn = True
    driver.find_element(By.PARTIAL_LINK_TEXT, "Joint Checking").click()
    time.sleep(3)

def allyLogout(driver):
    locateAllyWindow(driver)
    # Click Profile and Settings
    driver.webDriver.find_element(By.XPATH, "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p").click()
    # click Log out
    driver.webDriver.find_element(By.XPATH, "//*[@id='profile-menu-logout']/span").click()

def getAllyBalance(driver):
    locateAllyWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[1]/div/section[1]/div/div[1]/div/div[2]/div[1]/span[2]/span/div").text.replace('$', '').replace(',', '')

def captureAllyTransactions(driver, dateRange):
    def setAllyTransactionElementRoot(row, column):
        return "/html/body/div/div[1]/main/div/div/div/div[1]/section/div[2]/div/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"
    
    directory = setDirectory()
    allyActivity = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\ally.csv"
    open(allyActivity, 'w', newline='').truncate()
    row = 1
    column = 1
    element = setAllyTransactionElementRoot(row, column)
    time.sleep(6)
    insideDateRange = True
    while insideDateRange:
        try:
            date = datetime.strptime(driver.find_element(By.XPATH, element + "span").text, '%b %d, %Y').date()
            if date < dateRange[0] or date > dateRange[1]:
                insideDateRange = False
            else:
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                description = driver.find_element(By.XPATH, element + "div/button/span").text
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                amount = driver.find_element(By.XPATH, element + "span").text.replace('$', '').replace(',', '')
                # method to remove '-' from string since the above wasn't working
                if not amount[0].isnumeric():
                    amount = -Decimal(amount.replace(amount[0], ''))
                description = modifyTransactionDescription(description)
                transaction = str(date), description, amount
                csv.writer(open(allyActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                row += 1
                column = 1
                element = setAllyTransactionElementRoot(row, column)
        except (NoSuchElementException):
            insideDateRange = False
    return allyActivity

def runAlly(driver):
    today = datetime.today()
    dateRange = getStartAndEndOfDateRange(today, today.month, today.year, 7)
    Ally = USD("Ally")
    locateAllyWindow(driver)
    Ally.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver.webDriver, dateRange)
    importUniqueTransactionsToGnuCash(Ally, allyActivity, driver.webDriver, dateRange, 0)
    return Ally
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runAlly(driver)
    response.getData()
    allyLogout(driver)
