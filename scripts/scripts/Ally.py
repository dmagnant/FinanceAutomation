import csv
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook, importUniqueTransactionsToGnuCash
    from Functions.TransactionFunctions import modifyTransactionDescription
    from Functions.WebDriverFunctions import openWebDriver
else:
    from .Functions.GeneralFunctions import (closeExpressVPN, getPassword,
                                            getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from .Functions.GnuCashFunctions import openGnuCashBook, importUniqueTransactionsToGnuCash
    from .Functions.TransactionFunctions import modifyTransactionDescription
    from .Functions.WebDriverFunctions import openWebDriver

def allyLogin(driver):
    directory = setDirectory()
    # closeExpressVPN()
    driver.implicitly_wait(5)
    driver.execute_script("window.open('https://secure.ally.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)
    # login
    # enter password # changed 1/21/22
    driver.find_element(By.ID, "password").send_keys(getPassword(directory, 'Ally Bank'))
    time.sleep(1)
    # click Log In
    driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[1]/form/div[3]/button/span").click()
    time.sleep(5)
    # check if error message is seen
    try:
        driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div/div/b")
        loggedIn = False
    except NoSuchElementException:
        loggedIn = True
    return loggedIn

def getAllyBalance(driver):
    return driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[2]/div/div[2]/div/table/tbody/tr/td[3]/div").text.replace('$', '').replace(',', '')

def setAllyTransactionElementRoot(row, column):
    return "/html/body/div/div[1]/main/div/div/div/div[1]/section/div[2]/div/span/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"

def captureAllyTransactions(driver, dateRange, allyActivity):
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

def runAlly(driver):
    directory = setDirectory()
    loggedIn = allyLogin(driver)
    if loggedIn:
        ally = getAllyBalance(driver)
        allyActivity = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\ally.csv"
        open(allyActivity, 'w', newline='').truncate()
        dateRange = getStartAndEndOfDateRange(datetime.today(), datetime.today().month, datetime.today().year, 8)
        captureAllyTransactions(driver, dateRange, allyActivity)
        myBook = openGnuCashBook('Home', False, False)
        gnuAllyActivity = directory + r"\Projects\Coding\Python\BankingAutomation\Resources\gnu_ally.csv"
        open(gnuAllyActivity, 'w', newline='').truncate()
        # Compare against existing transactions in GnuCash and import new ones
        reviewTrans = importUniqueTransactionsToGnuCash('Ally', allyActivity, gnuAllyActivity, myBook, driver, directory, dateRange, 0)
    else:
        ally = 0.00
        reviewTrans = ''
    return [ally, reviewTrans]

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    response = runAlly(driver)
    print('balance: ' + str(response[0]))
    print('transactions to review: ' + str(response[1]))
