import csv, time
from datetime import datetime
from decimal import Decimal
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
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
    if not found:   allyLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    return True

def allyLogin(driver):
    loggedIn = False
    while not loggedIn:
        driver.openNewWindow('https://ally.com/')
        time.sleep(2)
        driver.webDriver.find_element(By.XPATH,"/html/body/header/section[1]/div/nav/ul/li[5]/button").click() # login
        time.sleep(2)
        try:    driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[4]/button").click() # login
        except ElementNotInteractableException:
            driver.webDriver.refresh(); time.sleep(1)
            driver.webDriver.find_element(By.XPATH,"/html/body/header/section[1]/div/nav/ul/li[5]/button").click() # login
            time.sleep(2)
            driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button").click() # login
        time.sleep(5)
        try: # check if login button is still seen
            driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[2]/form/div[3]/button/span").click()
            loggedIn = True
        except NoSuchElementException:  loggedIn = True
    driver.webDriver.find_element(By.PARTIAL_LINK_TEXT, "Joint Checking").click();  time.sleep(5)
    # driver.webDriver.find_element(By.XPATH,'/html/body/div/div[1]/main/div/div/div/div[1]/div/div/span/div[1]/button[1]/span').click()
    # time.sleep(1)
    
def allyLogout(driver):
    locateAllyWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p").click() # Profile and Settings
    driver.webDriver.find_element(By.XPATH, "//*[@id='profile-menu-logout']/span").click() # Log out

def getAllyBalance(driver):
    locateAllyWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[1]/div/section[1]/div/div[1]/div/div[2]/div[1]/span[2]/span/div").text.replace('$', '').replace(',', '')

def captureAllyTransactions(driver, dateRange):
    def setAllyTransactionElementRoot(row, column):
        return "/html/body/div[1]/div[1]/main/div/div/div/div[1]/div/div/div[2]/section[2]/div[2]/div/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"

    allyActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\ally.csv"
    open(allyActivity, 'w', newline='').truncate()
    row = column = 1
    element = setAllyTransactionElementRoot(row, column)
    time.sleep(6)
    insideDateRange = True
    while insideDateRange:
        try:
            date = datetime.strptime(driver.webDriver.find_element(By.XPATH, element + "span").text, '%b %d, %Y').date()
            if date < dateRange['startDate'] or date > dateRange['endDate']:    insideDateRange = False
            else:
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                description = driver.webDriver.find_element(By.XPATH, element + "div/button/span").text
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                amount = driver.webDriver.find_element(By.XPATH, element + "span").text.replace('$', '').replace(',', '')
                if not amount[0].isnumeric():   amount = -Decimal(amount.replace(amount[0], ''))
                description = modifyTransactionDescription(description)
                transaction = str(date), description, amount
                csv.writer(open(allyActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                row += 1
                column = 1
                element = setAllyTransactionElementRoot(row, column)
        except (NoSuchElementException):    insideDateRange = False
    return allyActivity

def runAlly(driver, account, book):
    dateRange = getStartAndEndOfDateRange(datetime.today().date(), 7)
    locateAllyWindow(driver)
    account.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver, dateRange)
    book.importUniqueTransactionsToGnuCash(account, allyActivity, driver, dateRange, 0)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Home')
    Ally = USD("Ally", book)
    runAlly(driver, Ally, book)
    Ally.getData()
    # allyLogout(driver)
    book.closeBook()

    # dateRange = getStartAndEndOfDateRange(datetime.today().date(), 7)
    # driver = Driver("Chrome")
    # book = GnuCash('Home')
    # locateAllyWindow(driver)