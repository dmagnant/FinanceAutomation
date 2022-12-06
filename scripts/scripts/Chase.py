import os
import time
from datetime import datetime
import pyautogui
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Chase":
    from Functions.GeneralFunctions import (setDirectory, showMessage)
    from Functions.GnuCashFunctions import (importGnuTransaction)
    from Classes.WebDriver import Driver
    from Classes.Asset import USD
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage)
    from .Functions.GnuCashFunctions import (importGnuTransaction)
    from .Classes.Asset import USD

def locateChaseWindow(driver):
    found = driver.findWindowByUrl("chase.com/web/auth")
    if not found:
        chaseLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def chaseLogin(driver):
    driver.implicitly_wait(5)
    driver.execute_script("window.open('https://secure07a.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/index');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(15)
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

def runChase(driver):
    directory = setDirectory()
    today = datetime.today()
    Chase = USD("Chase")
    locateChaseWindow(driver)
    Chase.setBalance(getChaseBalance(driver))
    transactionsCSV = exportChaseTransactions(driver.webDriver, today)
    claimChaseRewards(driver)
    importGnuTransaction(Chase, transactionsCSV, driver.webDriver)
    Chase.locateAndUpdateSpreadsheet(driver.webDriver)
    if Chase.reviewTransactions:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    showMessage("Balances + Review", f'Chase Balance: {Chase.balance} \n' f'GnuCash Chase Balance: {Chase.gnuBalance} \n \n' f'Review transactions:\n{Chase.reviewTransactions}')
    driver.close()

if __name__ == '__main__':
    driver = Driver("Chrome")
    runChase(driver)
