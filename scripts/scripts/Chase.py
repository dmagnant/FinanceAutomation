import time
from datetime import datetime

import pyautogui
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Chase":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash

def locateChaseWindow(driver):
    found = driver.findWindowByUrl("chase.com/web/auth")
    if not found:
        chaseLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def chaseLogin(driver):
    driver.webDriver.implicitly_wait(5)
    driver.openNewWindow('https://secure07a.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index')
    time.sleep(5)
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('enter')

def getChaseBalance(driver):
    locateChaseWindow(driver)    
    return driver.webDriver.find_element(By.ID, "accountCurrentBalanceLinkWithReconFlyoutValue").text.strip('$')

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
    time.sleep(1)
    driver.webDriver.get("https://ultimaterewardspoints.chase.com/cash-back?lang=en")
    time.sleep(2)
    # points balance
    balance = driver.webDriver.find_element(By.XPATH,"//*[@id='pointsBalanceId']/div/span[1]").text
    if float(balance) > 0:
        # Deposit into a Bank Account
        driver.webDriver.find_element(By.XPATH, "//*[@id='cashBackStart']/section[1]/div[2]/form/div[5]/div[1]/div[2]/selectable-tile/div/mds-fieldset/div/mds-selectable-tile/div/div/span").click()
        pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(2)
        driver.webDriver.find_element(By.ID, "main").click()
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.press('enter')                

def runChase(driver, account, book):
    today = datetime.today()
    locateChaseWindow(driver)
    account.setBalance(getChaseBalance(driver))
    transactionsCSV = exportChaseTransactions(driver.webDriver, today)
    claimChaseRewards(driver)
    book.importGnuTransaction(account, transactionsCSV, driver)
    account.locateAndUpdateSpreadsheet(driver)
    if account.reviewTransactions:
        book.openGnuCashUI()
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Chase = USD("Chase", book)    
    runChase(driver, Chase, book)
    Chase.getData()
    book.closeBook()
    