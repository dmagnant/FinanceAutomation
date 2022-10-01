import csv
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Sofi":
    from Functions.GeneralFunctions import (closeExpressVPN, getUsername, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook, importUniqueTransactionsToGnuCash
    from Functions.TransactionFunctions import modifyTransactionDescription
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from .Functions.GnuCashFunctions import openGnuCashBook, importUniqueTransactionsToGnuCash
    from .Functions.TransactionFunctions import modifyTransactionDescription
    from .Functions.WebDriverFunctions import findWindowByUrl


def sofiLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.sofi.com/login/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        # click LOG IN
        driver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click()
        time.sleep(1)
        # look for email is required error (suggesting that auto-fill didn't occur)
        driver.find_element(By.ID,"error-3")
        # username
        driver.find_element(By.ID, "username").send_keys(getUsername(directory, 'Sofi'))
        time.sleep(1)
        # # password
        driver.find_element(By.ID, "password").send_keys(getPassword(directory, 'Sofi'))
        time.sleep(1)
        # click LOG IN
        driver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click()
        showMessage("OTP Verification", "Enter code from phone, then click OK")
        # remember device
        driver.find_element(By.XPATH,"//*[@id='mainContent']/div/div/div[2]/form/div[2]/div[1]/label/span").click()
        # Verify code
        driver.find_element(By.ID,"verifyCode").click()
    except NoSuchElementException:
        exception = "logged in"

def getSofiBalanceAndOrientPage(driver, account):
    found = findWindowByUrl(driver, "sofi.com")
    if not found:
        sofiLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1) 
    driver.get("https://www.sofi.com/my/money/account/#/1000028154579/account-detail") if account == 'Checking' else driver.get("https://www.sofi.com/my/money/account/1000028154560/account-detail")
    time.sleep(2)
    table = 1
    div = '2' if account == 'Checking' else '3'
    def findBalanceElement(driver, table, div):
        xpath = "/html/body/div/main/div[3]/div[" + div + "]/table[" + str(table)  + "]/tbody/tr[1]/td[6]/span"
        return driver.find_element(By.XPATH, xpath).text.strip('$').replace(',', '')
    balance = findBalanceElement(driver, table, div)
    if balance == "": # Pending transactions will load as table 1 with a blank balance. if pending transactions exist, move to next Table
        table += 1
        balance = findBalanceElement(driver, table, div)
    return [balance, table, div]

def setSofiTransactionElementRoot(table, row, column, div):
    return "/html/body/div/main/div[3]/div[" + div + "]/table[" + str(table) + "]/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/span"

def getTransactionsFromSofiWebsite(driver, dateRange, sofiActivity, today, tableStart, div):
    year = today.year
    table = tableStart
    row = 1
    column = 1
    elementRoot = setSofiTransactionElementRoot(table, row, column, div)
    insideDateRange = True
    previousMonth = False
    
    while insideDateRange:
        try:
            # capture Date in 'Mon Day' format and add year
            sofiDate = datetime.strptime(driver.find_element(By.XPATH, elementRoot).text, '%b %d').date().replace(year=year)
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

def runSofiAccount(driver, dateRange, today, account):
    directory = setDirectory()
    balanceAndPageOrientation = getSofiBalanceAndOrientPage(driver, account)
    sofiActivity = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\sofi.csv"
    gnuSofiActivity = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\gnu_sofi.csv"
    open(sofiActivity, 'w', newline='').truncate()
    open(gnuSofiActivity, 'w', newline='').truncate()
    getTransactionsFromSofiWebsite(driver, dateRange, sofiActivity, today, balanceAndPageOrientation[1], balanceAndPageOrientation[2])
    myBook = openGnuCashBook('Finance', False, False)
    reviewTrans = importUniqueTransactionsToGnuCash('Sofi ' + account, sofiActivity, gnuSofiActivity, myBook, driver, directory, dateRange, 0)
    return [balanceAndPageOrientation[0], reviewTrans]

def runSofi(driver):
    sofiLogin(driver)
    today = datetime.today()
    dateRange = getStartAndEndOfDateRange(today, today.month, today.year, 5)
    checking = runSofiAccount(driver, dateRange, today, "Checking")
    savings = runSofiAccount(driver, dateRange, today, "Savings")
    # switch back to checking page
    driver.get("https://www.sofi.com/my/money/account/#/1000028154579/account-detail")
    return [checking, savings]

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    response = runSofi(driver)
    print('checking balance: ' + response[0][0])
    print('transactions to review: ' + response[0][1])
    print('savings balance: ' + response[1][0])
    print('transactions to review: ' + response[1][1])
