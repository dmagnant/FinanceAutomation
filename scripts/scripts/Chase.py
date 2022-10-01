import os
import time
from datetime import datetime

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Chase":
    from Functions.GeneralFunctions import (setDirectory, showMessage)
    from Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage)
    from .Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl

def locateChaseWindow(driver):
    found = findWindowByUrl(driver, "chase.com/web/auth")
    if not found:
        chaseLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)     

def chaseLogin(driver):
    driver.execute_script("window.open('https://www.chase.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])    
    time.sleep(2)
    # login
    showMessage("Login Manually", 'login manually \n' 'Then click OK \n')
    driver.get("https://secure07a.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/multiProduct;flyout=accountSummary,818208017,CARD,BAC")
    # time.sleep(2)

def getChaseBalance(driver):
    locateChaseWindow(driver)    
    return driver.find_element(By.ID, "accountCurrentBalanceLinkWithReconFlyoutValue").text.strip('$')

def exportChaseTransactions(driver, today):
    # click on Activity since last statement
    driver.find_element(By.XPATH, "//*[@id='header-transactionTypeOptions']/span[1]").click()
    # choose last statement
    driver.find_element(By.ID, "item-0-STMT_CYCLE_1").click()
    time.sleep(1)
    # click Download
    driver.find_element(By.XPATH, "//*[@id='downloadActivityIcon']").click()
    time.sleep(2)
    # click Download
    driver.find_element(By.ID, "download").click()

    year = today.year
    month = today.month
    day = today.strftime('%d')
    monthTo = today.strftime('%m')
    yearTo = str(year)
    monthFrom = "12"         if month == 1 else "{:02d}".format(month - 1)
    yearfrom = str(year - 1) if month == 1 else yearTo
    fromDate = yearfrom + monthFrom + "07_"
    toDate = yearTo + monthTo + "06_"
    currentDate = yearTo + monthTo + day
    return r'C:\Users\dmagn\Downloads\Chase2715_Activity' + fromDate + toDate + currentDate + '.csv'


def claimChaseRewards(driver):
    locateChaseWindow(driver)
    driver.get("https://ultimaterewardspoints.chase.com/cash-back?lang=en")
    try:
        # Deposit into a Bank Account
        driver.find_element(By.XPATH, "/html/body/the-app/main/ng-component/main/div/section[2]/div[2]/form/div[6]/ul/li[2]/label").click()
        # Click Continue
        driver.find_element(By.XPATH, "/html/body/the-app/main/ng-component/main/div/section[2]/div[2]/form/div[7]/button").click()
        # Click Confirm & Submit
        driver.find_element(By.ID, "cash_back_button_submit").click()
    except NoSuchElementException:
        exception = "caught"
    except ElementClickInterceptedException:
        exception = "caught"

def locateAndUpdateSpreadsheetForChase(driver, chase, today):
    directory = setDirectory()
    # switch worksheets if running in December (to next year's worksheet)
    month = today.month
    year = today.year
    if month == 12:
        year = year + 1
    chaseNeg = float(chase) * -1
    updateSpreadsheet(directory, 'Checking Balance', year, 'Chase', month, chaseNeg, 'Chase CC')
    updateSpreadsheet(directory, 'Checking Balance', year, 'Chase', month, chaseNeg, 'Chase CC', True)
    # Display Checking Balance spreadsheet
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=1688093622');")

def runChase(driver):
    directory = setDirectory()
    locateChaseWindow(driver)
    chase = getChaseBalance(driver)
    today = datetime.today()
    transactionsCSV = exportChaseTransactions(driver, today)
    claimChaseRewards(driver)
    myBook = openGnuCashBook('Finance', False, False)
    reviewTrans = importGnuTransaction('Chase', transactionsCSV, myBook, driver, directory)
    chaseGnu = getGnuCashBalance(myBook, 'Chase')
    locateAndUpdateSpreadsheetForChase(driver, chase, today)
    if reviewTrans:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    showMessage("Balances + Review", f'Chase Balance: {chase} \n' f'GnuCash Chase Balance: {chaseGnu} \n \n' f'Review transactions:\n{reviewTrans}')
    driver.quit()

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    runChase(driver)
