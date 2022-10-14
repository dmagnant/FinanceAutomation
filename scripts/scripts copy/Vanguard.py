import os
import time
from datetime import datetime
from decimal import Decimal

import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Vanguard":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getUsername, getPassword, getStartAndEndOfDateRange)
    from Functions.GnuCashFunctions import (openGnuCashBook, getGnuCashBalance, writeGnuTransaction)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getUsername, getPassword, getStartAndEndOfDateRange)
    from .Functions.GnuCashFunctions import (openGnuCashBook, getGnuCashBalance, writeGnuTransaction)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl
    

def locateVanguardWindow(driver):
    found = findWindowByUrl(driver, "ownyourfuture.vanguard.com/main")
    if not found:
        vanguardLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)

def vanguardLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://ownyourfuture.vanguard.com/login#/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    # Enter username
    driver.find_element(By.ID, "username").send_keys(getUsername(directory, 'Vanguard'))
    time.sleep(1)
    # Enter password
    driver.find_element(By.ID, "pword").send_keys(getPassword(directory, 'Vanguard'))
    time.sleep(1)
    # click Log in
    driver.find_element(By.XPATH, "//*[@id='vui-button-1']/button/div").click()
    # handle security code
    try:
        # look for security code box
        driver.find_element(By.ID, 'CODE')
        showMessage('Security Code', "Enter Security code, then click OK")
        # click remember me
        driver.find_element(By.XPATH,"//*[@id='radioGroupId-bind-selection-group']/c11n-radio[1]/label/div").click()
        # click Verify
        driver.find_element(By.XPATH, "//*[@id='security-code-submit-btn']/button/span/span").click()
    except NoSuchElementException:
        exception = "caught"


def getVanguardBalanceAndInterestYTD(driver):
    locateVanguardWindow(driver)    
    # navigate to asset details page (click view all assets)
    driver.get('https://ownyourfuture.vanguard.com/main/dashboard/assets-details')
    time.sleep(2)
    # move cursor to middle window
    pyautogui.moveTo(500, 500)
    #scroll down
    pyautogui.scroll(-1000)
    # Get Total Account Balance
    pensionBalance = driver.find_element(By.XPATH, "/html/body/div[3]/div/app-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[3]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    # Get Interest YTD
    interestYTD = driver.find_element(By.XPATH, "/html/body/div[3]/div/app-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[4]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    return [pensionBalance, interestYTD]


def importGnuTransactions(myBook, today, balances):
    #get current date
    year = today.year
    month = today.month
    lastMonth = getStartAndEndOfDateRange(today, month, year, "month")
    interestAmount = 0
    pension = getGnuCashBalance(myBook, 'VanguardPension')
    pensionAcct = "Assets:Non-Liquid Assets:Pension"
    with myBook as book:
        # # GNUCASH
        # retrieve transactions from GnuCash
        transactions = [tr for tr in book.transactions
                        if str(tr.post_date.strftime('%Y')) == str(lastMonth[0].year)
                        for spl in tr.splits
                        if spl.account.fullname == pensionAcct
                        ]
        for tr in transactions:
            date = str(tr.post_date.strftime('%Y'))
            for spl in tr.splits:
                if spl.account.fullname == "Income:Investments:Interest":
                    interestAmount = interestAmount + abs(spl.value)
        accountChange = Decimal(balances[0]) - pension
        interest = Decimal(balances[1]) - interestAmount
        employerContribution = accountChange - interest
        writeGnuTransaction(myBook, "Contribution + Interest", lastMonth[1], [-interest, -employerContribution, accountChange], pensionAcct)   
    book.close()

    return [interest, employerContribution]

def runVanguard(driver):
    directory = setDirectory()
    locateVanguardWindow(driver)
    balanceAndInterestYTD = getVanguardBalanceAndInterestYTD(driver)
    myBook = openGnuCashBook('Finance', False, False)
    today = datetime.today()
    values = importGnuTransactions(myBook, today, balanceAndInterestYTD)
    vanguardGnu = getGnuCashBalance(myBook, 'VanguardPension')
    updateSpreadsheet(directory, 'Asset Allocation', today.year, 'VanguardPension', today.month, float(balanceAndInterestYTD[0]))
    os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=2058576150');")
    showMessage("Balances",f'Pension Balance: {balanceAndInterestYTD[0]} \n'f'GnuCash Pension Balance: {vanguardGnu} \n'f'Interest earned: {values[0]} \n'f'Total monthly contributions: {values[1]} \n')

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    runVanguard(driver)
    