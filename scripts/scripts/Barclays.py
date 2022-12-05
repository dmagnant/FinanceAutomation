import os
import time
from datetime import datetime
from typing import KeysView

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Barclays":
    from Functions.GeneralFunctions import (getPassword, getUsername, setDirectory, showMessage)
    from Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Classes.WebDriver import Driver
    from Classes.Asset import USD
else:
    from .Functions.GeneralFunctions import (getPassword, getUsername, setDirectory, showMessage)
    from .Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Classes.Asset import USD

def locateBarclaysWindow(driver):
    found = driver.findWindowByUrl("barclaycardus.com")
    if not found:
        barclaysLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)     

def barclaysLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.barclaycardus.com/servicing/home?secureLogin=');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])    
    # Login
    driver.find_element(By.ID, "username").send_keys(getUsername(directory, 'Barclay Card'))
    time.sleep(2)
    driver.find_element(By.ID, "password").send_keys(getPassword(directory, 'Barclay Card'))
    time.sleep(2)
    driver.find_element(By.ID, "loginButton").click()
    # handle security questions
    try:
        question1 = driver.find_element(By.ID, "question1TxtbxLabel").text
        question2 = driver.find_element(By.ID, "question2TxtbxLabel").text
        q1 = "In what year was your mother born?"
        a1 = os.environ.get('MotherBirthYear')
        q2 = "What is the name of the first company you worked for?"
        a2 = os.environ.get('FirstEmployer')
        if question1 == q1:
            driver.find_element(By.ID, "rsaAns1").send_keys(a1)
            driver.find_element(By.ID, "rsaAns2").send_keys(a2)
        else:
            driver.find_element(By.ID, "rsaAns1").send_keys(a2)
            driver.find_element(By.ID, "rsaAns2").send_keys(a1)
        driver.find_element(By.ID, "rsaChallengeFormSubmitButton").click()
    except NoSuchElementException:
        exception = "Caught"
    # handle Confirm Your Identity
    try:
        driver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div/div/div[2]/div[1]/label/span").click()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        # User pop-up to enter SecurPass Code
        showMessage("Get Code From Phone", "Enter in box, then click OK")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
    except NoSuchElementException:
        exception = "Caught"
    # handle Pop-up
    try:
        driver.find_element(By.XPATH, "/html/body/div[4]/div/button/span").click()
    except NoSuchElementException:
        exception = "Caught"

def getBarclaysBalance(driver):
    locateBarclaysWindow(driver)     
    return driver.webDriver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div[2]/div[1]/section[1]/div/div/div[2]/div/div[2]/div[1]/div").text.strip('-').strip('$')

def exportBarclaysTransactions(driver, today):
    # # EXPORT TRANSACTIONS
    # click on Activity & Statements
    driver.find_element(By.XPATH, "/html/body/section[2]/div[1]/nav/div/ul/li[3]/a").click()
    # Click on Transactions
    driver.find_element(By.XPATH, "/html/body/section[2]/div[1]/nav/div/ul/li[3]/ul/li/div/div[2]/ul/li[1]/a").click()
    # Click on Download
    driver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div/div/div[3]/div[1]/div/div[2]/span/div/button/span[1]").click()
    year = today.year
    month = today.month
    monthTo = str(month)
    if month == 1:
        monthFrom = "12"
        yrTO = str(year - 2000)
        yearTo = str(year)
        yrFROM = str(year - 2001)
        yearFrom = str(year - 1)
    else:
        monthFrom = str(month - 1)
        yrTO = str(year - 2000)
        yearTo = str(year)
        yrFROM = yrTO
        yearFrom = yearTo
    fromDate = monthFrom + "/11/" + yrFROM
    toDate = monthTo + "/10/" + yrTO
    # enter date_range
    driver.find_element(By.ID, "downloadFromDate_input").send_keys(fromDate)
    driver.find_element(By.ID, "downloadToDate_input").send_keys(toDate)
    # click Download
    driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div/div/div[2]/div/form/div[3]/div/button").click()
    time.sleep(2)
    return r"C:\Users\dmagn\Downloads\CreditCard_" + yearFrom + monthFrom + "11_" + yearTo + monthTo + "10.csv"

def claimBarclaysRewards(driver):
    locateBarclaysWindow(driver)      
    # # REDEEM REWARDS
    # click on Rewards & Benefits
    driver.webDriver.find_element(By.XPATH, "/html/body/section[2]/div[1]/nav/div/ul/li[4]/a").click()
    # click on Redeem my cash rewards
    driver.webDriver.find_element(By.XPATH, "//*[@id='rewards-benefits-container']/div[1]/ul/li[3]/a").click()
    # click on Direct Deposit or Statement Credit
    driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/ul/li[1]/div/a").click()
    # click on Continue
    driver.webDriver.find_element(By.ID, "redeem-continue").click()
    # Click "select an option" (for method of rewards)
    driver.webDriver.find_element(By.XPATH, "//*[@id='mor_dropDown0']").click()
    driver.webDriver.find_element(By.XPATH, "//*[@id='mor_dropDown0']").send_keys(KeysView.DOWN)
    driver.webDriver.find_element(By.XPATH, "//*[@id='mor_dropDown0']").send_keys(KeysView.ENTER)
    time.sleep(1)
    # Click Continue
    driver.webDriver.find_element(By.XPATH, "//*[@id='achModal-continue']").click()
    time.sleep(1)
    # click on Redeem Now
    driver.webDriver.find_element(By.XPATH, "/html/body/section[2]/div[4]/div[2]/cashback/div/div[2]/div/ui-view/redeem/div/review/div/div/div/div/div[2]/form/div[3]/div/div[1]/button").click()

def runBarclays(driver):
    directory = setDirectory()
    today = datetime.today()
    myBook = openGnuCashBook('Finance', False, False)
    Barclays = USD("Barclays")
    locateBarclaysWindow(driver)
    Barclays.setBalance(getBarclaysBalance(driver))
    rewardsBalance = float(driver.find_element(By.XPATH, "//*[@id='rewardsTile']/div[2]/div/div[2]/div[1]/div").text.strip('$'))
    transactionsCSV = exportBarclaysTransactions(driver.webDriver, today)
    if rewardsBalance > 50:
        claimBarclaysRewards(driver, rewardsBalance)
    reviewTrans = importGnuTransaction(Barclays.name, transactionsCSV, myBook, driver.webDriver, 5)
    Barclays.setReviewTransactions(reviewTrans)
    Barclays.updateGnuBalance(myBook)
    Barclays.locateAndUpdateSpreadsheet(driver.webDriver)
    if Barclays.reviewTransactions:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    showMessage("Balances + Review", f'Barclays balance: {Barclays.balance} \n' f'GnuCash Barclays balance: {Barclays.gnuBalance} \n \n' f'Review transactions:\n{Barclays.reviewTransactions}')
    driver.close()

if __name__ == '__main__':
    driver = Driver("Chrome")
    runBarclays(driver)
