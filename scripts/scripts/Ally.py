import csv
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash
    from Functions.TransactionFunctions import modifyTransactionDescription
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                             getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash
    from .Functions.TransactionFunctions import modifyTransactionDescription

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
    # check if error message is seen
    try:
        driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div/div/b")
        loggedIn = False
    except NoSuchElementException:
        loggedIn = True
    return loggedIn

def allyLogout(driver):
    locateAllyWindow(driver)
    # Click Profile and Settings
    driver.webDriver.find_element(By.XPATH, "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p").click()
    # click Log out
    driver.webDriver.find_element(By.XPATH, "//*[@id='profile-menu-logout']/span").click()

def getAllyBalance(driver):
    locateAllyWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[2]/div/div[1]/div[2]/div/table/tbody/tr/td[3]/div").text.replace('$', '').replace(',', '')

def setAllyTransactionElementRoot(row, column):
    return "/html/body/div/div[1]/main/div/div/div/div[1]/section/div[2]/div/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"

def captureAllyTransactions(driver, dateRange):
    directory = setDirectory()
    allyActivity = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\ally.csv"
    open(allyActivity, 'w', newline='').truncate()
     # click Joint Checking link
    driver.find_element(By.PARTIAL_LINK_TEXT, "Joint Checking").click()
    time.sleep(3)
    row = 1
    column = 1
    element = setAllyTransactionElementRoot(row, column)
    time.sleep(6)
    insideDateRange = True
    while insideDateRange:
        try:
            date = datetime.strptime(driver.find_element(By.XPATH, element + "span").text, '%b %d, %Y').date()
            if date < dateRange[0] or date > dateRange[1]:
            # if str(modDate) not in dateRange:
                insideDateRange = False
            else:
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                description = driver.find_element(By.XPATH, element + "div/button/span").text
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                amount = driver.find_element(By.XPATH, element + "span").text.replace('$','').replace(',','')
                description = modifyTransactionDescription(description)
                transaction = str(date), description, amount
                csv.writer(open(allyActivity, 'a', newline='')).writerow(transaction)
                row += 1
                column = 1
                element = setAllyTransactionElementRoot(row, column)
        except (NoSuchElementException, ValueError):
            insideDateRange = False
    return allyActivity

def runAlly(driver):
    today = datetime.today()
    dateRange = getStartAndEndOfDateRange(today, today.month, today.year, 7)
    Ally = USD("Ally")
    locateAllyWindow(driver)
    Ally.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver.webDriver, dateRange)
    importUniqueTransactionsToGnuCash('Ally', allyActivity, driver.webDriver, dateRange, 0)
    return Ally
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runAlly(driver)
    response.getData()
    allyLogout(driver)
