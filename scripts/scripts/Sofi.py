import csv
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Sofi":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, setDirectory,
                                            showMessage)
    from Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                             getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import importUniqueTransactionsToGnuCash, modifyTransactionDescription

def locateSofiWindow(driver):
    found = driver.findWindowByUrl("sofi.com")
    if not found:
        sofiLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1) 

def sofiLogin(driver):
    driver.openNewWindow('https://login.sofi.com/u/login?state=hKFo2SBrOGMtTVZSUHZPalVPbEUyZmJyWXhyV3pYMU9lSzhEUKFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIGptNWpvQnRQQlFtSHFJT216N0dfLU1aZFBUbWFqVXl6o2NpZNkgNkxuc0xDc2ZGRUVMbDlTQzBDaWNPdkdlb2JvZXFab2I')
    driver = driver.webDriver
    time.sleep(2)
    # click Login
    driver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click()
    # # click LOG IN
    # driver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click()
    # time.sleep(1)
    # # look for email is required error (suggesting that auto-fill didn't occur)
    # driver.find_element(By.ID,"error-3")
    # # username
    # driver.find_element(By.ID, "username").send_keys(getUsername('Sofi'))
    # time.sleep(1)
    # # # password
    # driver.find_element(By.ID, "password").send_keys(getPassword('Sofi'))
    # time.sleep(1)
    # # click LOG IN
    # driver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click()
    try:
        driver.find_element(By.ID,'code')
        showMessage("OTP Verification", "Enter code from phone, then click OK")
        driver.find_element(By.XPATH,"//*[@id='mainContent']/div/div/div[2]/div[3]/div[1]/label/span").click() # remember device
        driver.find_element(By.ID,"verifyCode").click()
    except NoSuchElementException:
        exception = 'otp not required'

def sofiLogout(driver):
    locateSofiWindow(driver)
    driver.webDriver.get("https://www.sofi.com/member-home")
    # click Name on top right
    driver.webDriver.find_element(By.XPATH, "//*[@id='root']/header/nav/div[3]/div[2]/button").click()
    # click Log out
    driver.webDriver.find_element(By.XPATH, "//*[@id='user-dropdown']/div/div/a[4]").click()

def getSofiBalanceAndOrientPage(driver, account):
    locateSofiWindow(driver)
    driver.webDriver.get("https://www.sofi.com/my/money/account/1000028154579/account-detail") if 'checking' in account.name.lower() else driver.webDriver.get("https://www.sofi.com/my/money/account/1000028154560/account-detail")
    time.sleep(2)
    table = 1
    div = '2' if 'checking' in account.name.lower() else '3'
    def findBalanceElement(webDriver, table, div):
        xpath = "/html/body/div/main/div[3]/div[" + div + "]/table[" + str(table)  + "]/tbody/tr[1]/td[6]/span"
        return webDriver.find_element(By.XPATH, xpath).text.strip('$').replace(',', '')
    balance = findBalanceElement(driver.webDriver, table, div)
    if balance == "": # Pending transactions will load as table 1 with a blank balance. if pending transactions exist, move to next Table
        table += 1
        balance = findBalanceElement(driver.webDriver, table, div)
    account.setBalance(balance)
    return [table, div]

def setSofiTransactionElementRoot(table, row, column, div):
    return "/html/body/div/main/div[3]/div[" + div + "]/table[" + str(table) + "]/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/span"

def getTransactionsFromSofiWebsite(driver, dateRange, today, tableStart, div):
    sofiActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\sofi.csv"
    open(sofiActivity, 'w', newline='').truncate()
    year = today.year
    table = tableStart
    row = 1
    column = 1
    elementRoot = setSofiTransactionElementRoot(table, row, column, div)
    insideDateRange = True
    previousMonth = False
    while insideDateRange:
        try:
            try:
                # capture Date in 'Mon Day' format and add year
                sofiDate = datetime.strptime(driver.find_element(By.XPATH, elementRoot).text, '%b %d').date().replace(year=year)
            except ValueError:
                # capture Date in 'M/D/YY' format
                sofiDate = datetime.strptime(driver.find_element(By.XPATH, elementRoot).text, "%m/%d/%y").date()
            if sofiDate < dateRange[0] or sofiDate > dateRange[1]:
                insideDateRange = False
            else:
                column += 1
                description = driver.find_element(By.XPATH, setSofiTransactionElementRoot(table, row, column, div)).text
                column += 3
                amount = driver.find_element(By.XPATH, setSofiTransactionElementRoot(table, row, column, div)).text.replace('$', '').replace(',', '')
                description = modifyTransactionDescription(description, amount)
                transaction = sofiDate, description, amount
                csv.writer(open(sofiActivity, 'a', newline='')).writerow(transaction)
                row += 1
                column = 1
                elementRoot = setSofiTransactionElementRoot(table, row, column, div)
        except NoSuchElementException:
            if not previousMonth:
                table += 1
                row = 1
                column = 1
                elementRoot = setSofiTransactionElementRoot(table, row, column, div)
                previousMonth = True
            else:
                insideDateRange = False
    return sofiActivity

def runSofiAccount(driver, dateRange, today, account):
    tableAndDiv = getSofiBalanceAndOrientPage(driver, account)
    sofiActivity = getTransactionsFromSofiWebsite(driver.webDriver, dateRange, today, tableAndDiv[0], tableAndDiv[1])
    importUniqueTransactionsToGnuCash(account, sofiActivity, driver.webDriver, dateRange, 0)

def runSofi(driver):
    today = datetime.today().date()
    dateRange = getStartAndEndOfDateRange(today, 7)
    locateSofiWindow(driver)
    Checking = USD("Sofi Checking")
    Savings = USD("Sofi Savings")
    for account in [Checking, Savings]:
        runSofiAccount(driver, dateRange, today, account)
    driver.webDriver.get("https://www.sofi.com/my/money/account/#/1000028154579/account-detail") # switch back to checking page
    return [Checking, Savings]

if __name__ == '__main__':
    driver = Driver("Chrome")
    response = runSofi(driver)
    for accounts in response:
        accounts.getData()
    sofiLogout(driver)