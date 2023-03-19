import csv
import time
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange, setDirectory, showMessage)
    from Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription
elif __name__ == 'scripts.Ally':
    from scripts.Classes.Asset import USD
    from scripts.Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                             getStartAndEndOfDateRange, showMessage, setDirectory)
    from scripts.Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription    
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                             getStartAndEndOfDateRange, showMessage, setDirectory)
    from .Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription

def locateAllyWindow(driver):
    found = driver.findWindowByUrl("secure.ally.com")
    if not found:
        allyLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
    return True

def allyLogin(driver):
    # closeExpressVPN()
    driver.webDriver.implicitly_wait(10)
    loggedIn = False
    while not loggedIn:
        driver.openNewWindow('https://ally.com/')
        time.sleep(1)
        # click Login
        driver.webDriver.find_element(By.ID,"login").click()
        # enter Password (username already filled in)
        driver.webDriver.find_element(By.ID,"allysf-login-v2-password-367761b575af35f6ccb5b53e96b2fa2d").send_keys(getPassword('Ally Bank'))
        # click Login
        driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button").click()
        time.sleep(5)
        # check if login button is still seen
        try:
            driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[1]/form/div[3]/button/span")
            loggedIn = False
            driver.webDriver.close()
            driver.getLastWindow()
        except NoSuchElementException:
            loggedIn = True
    driver.webDriver.find_element(By.PARTIAL_LINK_TEXT, "Joint Checking").click()
    time.sleep(5)
    driver.webDriver.find_element(By.XPATH,'/html/body/div/div[1]/main/div/div/div/div[1]/div/div/span/div[1]/button[1]/span').click()
    time.sleep(1)
    
def allyLogout(driver):
    locateAllyWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p").click() # Profile and Settings
    driver.webDriver.find_element(By.XPATH, "//*[@id='profile-menu-logout']/span").click() # Log out

def getAllyBalance(driver):
    locateAllyWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[1]/div/section[1]/div/div[1]/div/div[2]/div[1]/span[2]/span/div").text.replace('$', '').replace(',', '')

def captureAllyTransactions(driver, dateRange):
    def setAllyTransactionElementRoot(row, column):
        return "/html/body/div/div[1]/main/div/div/div/div[1]/div/div/span/div[3]/section[2]/div[2]/div/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"
    
    allyActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\ally.csv"
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

def runAlly(driver, account):
    dateRange = getStartAndEndOfDateRange(datetime.today().date(), 7)
    locateAllyWindow(driver)
    account.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver.webDriver, dateRange)
    importUniqueTransactionsToGnuCash(account, allyActivity, driver.webDriver, dateRange, 0)
    
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    Ally = USD("Ally")
    runAlly(driver, Ally)
    Ally.getData()
    allyLogout(driver)
    