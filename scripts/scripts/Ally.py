import csv
import time
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange, setDirectory, showMessage, modifyTransactionDescription)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange, showMessage, setDirectory, modifyTransactionDescription)

def locateAllyWindow(driver):
    found = driver.findWindowByUrl("secure.ally.com")
    if not found:
        allyLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
    return True

def allyLogin(driver):
    driver.webDriver.implicitly_wait(10)
    loggedIn = False
    while not loggedIn:
        print('logging in')
        driver.openNewWindow('https://ally.com/')
        time.sleep(2)
        driver.webDriver.find_element(By.ID,"login").click() # login
        time.sleep(2)
        driver.webDriver.find_element(By.ID,"allysf-login-v2-password-367761b575af35f6ccb5b53e96b2fa2d").send_keys(getPassword('Ally Bank'))
        driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button").click() # login
        time.sleep(5)
        try: # check if login button is still seen
            driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[2]/form/div[3]/button/span").click()
            loggedIn = True
            # driver.webDriver.close()
            # driver.switchToLastWindow()
        except NoSuchElementException:
            print('not found')
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
            date = datetime.strptime(driver.webDriver.find_element(By.XPATH, element + "span").text, '%b %d, %Y').date()
            if date < dateRange['startDate'] or date > dateRange['endDate']:
                insideDateRange = False
            else:
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                description = driver.webDriver.find_element(By.XPATH, element + "div/button/span").text
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                amount = driver.webDriver.find_element(By.XPATH, element + "span").text.replace('$', '').replace(',', '')
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

def runAlly(driver, account, book):
    dateRange = getStartAndEndOfDateRange(datetime.today().date(), 7)
    locateAllyWindow(driver)
    account.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver, dateRange)
    book.importUniqueTransactionsToGnuCash(account, allyActivity, driver, dateRange, 0)
    
if __name__ == '__main__':
    # driver = Driver("Chrome")
    # book = GnuCash('Home')
    # Ally = USD("Ally", book)
    # runAlly(driver, Ally, book)
    # Ally.getData()
    # allyLogout(driver)
    # book.closeBook()
    
    # today = datetime.today().date()
    # timeSpan = 7
    
    # dateRange = getStartAndEndOfDateRange(today, timeSpan)
    
    driver = Driver("Chrome")
    found = driver.findWindowByUrl("we-energies.com")
    driver.webDriver.switch_to.window(found)
    time.sleep(1)
    billRow = 2
    billColumn = 7
    billFound = "no"
    # capture date
    weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
    weBillAmount = driver.webDriver.find_element(By.XPATH, weBillPath).text
    print(weBillAmount)