import time
from datetime import datetime
from decimal import Decimal

import pyautogui
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Vanguard":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook, writeGnuTransaction, openGnuCashUI
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange,
                                             getUsername, showMessage)
    from .Functions.GnuCashFunctions import (openGnuCashBook,
                                             writeGnuTransaction, openGnuCashUI)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
    
def locateVanguardWindow(driver):
    found = driver.findWindowByUrl("ownyourfuture.vanguard.com/main")
    if not found:
        vanguardLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def vanguardLogin(driver):
    driver.openNewWindow('https://ownyourfuture.vanguard.com/login#/')
    driver = driver.webDriver
    # Enter username
    driver.find_element(By.ID, "username").send_keys(getUsername('Vanguard'))
    time.sleep(1)
    # Enter password
    driver.find_element(By.ID, "pword").send_keys(getPassword('Vanguard'))
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

def getVanguardBalanceAndInterestYTD(driver, account):
    locateVanguardWindow(driver)    
    # navigate to asset details page (click view all assets)
    driver.webDriver.get('https://ownyourfuture.vanguard.com/main/dashboard/assets-details')
    time.sleep(2)
    # move cursor to middle window
    pyautogui.moveTo(500, 500)
    #scroll down
    pyautogui.scroll(-1000)
    # Get Total Account Balance
    pensionBalance = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[3]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    account.setBalance(pensionBalance)
    # Get Interest YTD
    interestYTD = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[4]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    return interestYTD

def importGnuTransactions(myBook, today, account, interestYTD):
    lastMonth = getStartAndEndOfDateRange(today, "month")
    interestAmount = 0
    # pension = getGnuCashBalance(myBook, 'VanguardPension')
    # pensionAcct = "Assets:Non-Liquid Assets:Pension"
    with myBook as book:
        # # GNUCASH
        # retrieve transactions from GnuCash
        transactions = [tr for tr in book.transactions
                        if str(tr.post_date.strftime('%Y')) == str(lastMonth[0].year)
                        for spl in tr.splits
                        if spl.account.fullname == account.gnuAccount
                        ]
        for tr in transactions:
            date = str(tr.post_date.strftime('%Y'))
            for spl in tr.splits:
                if spl.account.fullname == "Income:Investments:Interest":
                    interestAmount = interestAmount + abs(spl.value)
        accountChange = Decimal(account.balance) - account.gnuBalance
        interest = Decimal(interestYTD) - interestAmount
        employerContribution = accountChange - interest
        writeGnuTransaction(myBook, "Contribution + Interest", lastMonth[1], [-interest, -employerContribution, accountChange], account.gnuAccount)   
    book.close()
    return [interest, employerContribution]

def runVanguard(driver):
    today = datetime.today().date()
    myBook = openGnuCashBook('Finance', False, False)
    VanguardPension = USD("VanguardPension")
    locateVanguardWindow(driver)
    interestYTD = getVanguardBalanceAndInterestYTD(driver, VanguardPension)
    interestAndEmployerContribution = importGnuTransactions(myBook, today, VanguardPension, interestYTD)
    VanguardPension.updateGnuBalance(myBook)
    openSpreadsheet(driver, 'Asset Allocation', '2022')
    updateSpreadsheet('Asset Allocation', today.year, 'VanguardPension', today.month, float(VanguardPension.balance))
    openGnuCashUI('Finances')
    showMessage("Balances",f'Pension Balance: {VanguardPension.balance} \n'f'GnuCash Pension Balance: {VanguardPension.gnuBalance} \n'f'Interest earned: {interestAndEmployerContribution[0]} \n'f'Total monthly contributions: {interestAndEmployerContribution[1]} \n')

if __name__ == '__main__':
    driver = Driver("Chrome")
    runVanguard(driver)
    