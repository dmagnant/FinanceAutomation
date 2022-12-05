import os
import time
from datetime import datetime

from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "BoA":
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

def locateBoAWindowAndOpenAccount(driver, account):
    found = driver.findWindowByUrl("secure.bankofamerica.com")
    if not found:
        boALogin(driver.webDriver, account)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
        
def boALogin(driver, account):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.bankofamerica.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])   
    # login
    driver.find_element(By.ID, "onlineId1").send_keys(getUsername(directory, 'BoA CC'))
    driver.find_element(By.ID, "passcode1").send_keys(getPassword(directory, 'BoA CC'))
    driver.find_element(By.XPATH, "//*[@id='signIn']").click()
    # handle ID verification
    try:
        driver.find_element(By.XPATH, "//*[@id='btnARContinue']/span[1]").click()
        showMessage("Get Verification Code", "Enter code, then click OK")
        driver.find_element(By.XPATH, "//*[@id='yes-recognize']").click()
        driver.find_element(By.XPATH, "//*[@id='continue-auth-number']/span").click()
    except NoSuchElementException:
        exception = "Caught"
    # handle security questions
    try:
        question = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/div[2]/label").text
        q1 = "What is the name of a college you applied to but didn't attend?"
        a1 = os.environ.get('CollegeApplied')
        q2 = "As a child, what did you want to be when you grew up?"
        a2 = os.environ.get('DreamJob')
        q3 = "What is the name of your first babysitter?"
        a3 = os.environ.get('FirstBabySitter')
        if driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/div[2]/label"):
            question = driver.find_element(By.XPATH, 
                "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/div[2]/label").text
            if question == q1:
                driver.find_element(By.NAME, "challengeQuestionAnswer").send_keys(a1)
            elif question == q2:
                driver.find_element(By.NAME, "challengeQuestionAnswer").send_keys(a2)
            else:
                driver.find_element(By.NAME, "challengeQuestionAnswer").send_keys(a3)
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/fieldset/div[2]/div/div[1]/input").click()
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/form/a[1]/span").click()
    except NoSuchElementException:
        exception = "Caught"

    # close mobile app pop-up
    try:
        driver.find_element(By.XPATH, "//*[@id='sasi-overlay-module-modalClose']/span[1]").click()
    except NoSuchElementException:
        exception = "Caught"
    partialLink = 'Customized Cash Rewards Visa Signature - 8549' if account == "Personal" else 'Travel Rewards Visa Signature - 8955'
    driver.find_element(By.PARTIAL_LINK_TEXT, partialLink).click()
    time.sleep(3)

def getBoABalance(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[3]/div[4]/div[3]/div/div[2]/div[2]/div[2]").text.replace('$','').replace(',','')

def exportBoATransactions(driver, account, today):
    # click Previous transactions
    driver.find_element(By.PARTIAL_LINK_TEXT, "Previous transactions").click()
    # click Download, select microsoft excel
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[1]/a").click()
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[3]/div[1]/select").send_keys("m")
    driver.execute_script("window.scrollTo(0, 300)")
    # click Download Transactions
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[4]/div[1]/div/div[5]/div[2]/div[2]/div/div[3]/div/div[4]/div[2]/a/span").click()
    year = today.year
    stmtMonth = today.strftime("%B")
    stmtYear = str(year)
    accountNum = "_8549.csv" if account == "Personal" else "_8955.csv"
    return os.path.join(r"C:\Users\dmagn\Downloads", stmtMonth + stmtYear + accountNum)

def claimBoARewards(driver, account):
    locateBoAWindowAndOpenAccount(driver, account)
    driver = driver.webDriver
    driver.implicitly_wait(10)
    if account == "Personal":
        # # REDEEM REWARDS
        # click on View/Redeem menu
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[3]/a").click()
        time.sleep(5)
        #scroll down to view button
        driver.execute_script("window.scrollTo(0, 300)")
        time.sleep(3)
        # wait for Redeem Cash Rewards button to load, click it
        driver.find_element(By.ID, "rewardsRedeembtn").click()
        # switch to last window
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        # close out of pop-up (if present)
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/button").click()
        except NoSuchElementException:
            exception = "caught"
        # if no pop-up, proceed to click on Redemption option
        driver.find_element(By.ID, "redemption_option").click()
        # redeem if there is a balance, else skip
        try:
            # Choose Visa - statement credit
            driver.find_element(By.ID, "redemption_option").send_keys("v")
            driver.find_element(By.ID, "redemption_option").send_keys(Keys.ENTER)
            # click on Redeem all
            driver.find_element(By.ID, "redeem-all").click()
            # click Complete Redemption
            driver.find_element(By.ID, "complete-otr-confirm").click()
        except ElementNotInteractableException:
            exception = "caught"
    elif account == 'Joint': # may need to address minimum of 2500 points restriction
        # click View/Redeem
        driver.find_element(By.XPATH,"/html/body/div[1]/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div[4]/div[2]/a").click()
        # click Redeem Points
        driver.find_element(By.ID,"redeemButton").click()
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        # click Redeem
        driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]/a").click()
        # Available points        
        availablePoints = driver.find_element(By.ID,"summary_availablepoints").text.replace(',','')
        remainingPoints = availablePoints
        num = 4
        if int(availablePoints) > 0:
            while remainingPoints:
                # click select to redeem
                driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[6]/label/input").click()
                # capture remaining points
                remainingPoints = driver.find_element(By.ID,"remainingpoints").text.replace(',','')
                if remainingPoints == '':
                    break
                num += 2
                availablePoints = remainingPoints
            # click on "enter points to redeem"
            driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").click()
            # delete contents of input box
            backspaces = 8
            while backspaces > 0:
                driver.find_element(By.XPATH, "/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").send_keys(Keys.BACKSPACE)
                backspaces -= 1
            # fill with the points left
            driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[2]").send_keys(availablePoints)
            # click Update
            driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[2]/div/form/div/table/tbody/tr[" + str(num) + "]/td[7]/div/input[3]").click()
            # click Request Travel Credit
            driver.find_element(By.XPATH,"/html/body/main/div/div[2]/div/div[1]/div/div[2]/table/tbody/tr[7]/td/div/input").click()
            # click Complete redemption
            driver.find_element(By.XPATH,"/html/body/div[2]/div[2]/div[1]/div[1]/div[4]/input[1]").click()

def runBoA(driver, account):
    directory = setDirectory()
    today = datetime.today()
    myBook = openGnuCashBook('Finance', False, False) if account == "Personal" else openGnuCashBook('Home', False, False)
    importAccount = 'BoA' if account == "Personal" else 'BoA-joint'
    BoA = USD(importAccount)
    locateBoAWindowAndOpenAccount(driver, account)
    BoA.setBalance(getBoABalance(driver, account))
    transactionsCSV = exportBoATransactions(driver.webDriver, account, today)
    claimBoARewards(driver, account)
    reviewTrans = importGnuTransaction(importAccount, transactionsCSV, myBook, driver.webDriver)
    BoA.setReviewTransactions(reviewTrans)
    BoA.updateGnuBalance(myBook)
    BoA.locateAndUpdateSpreadsheet(driver.webDriver)
    if BoA.reviewTransactions:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash") if account == "Personal" else os.startfile(directory + r"\Stuff\Home\Finances\Home.gnucash")
    showMessage("Balances + Review", f'BoA Balance: {BoA.balance} \n' f'GnuCash BoA Balance: {BoA.gnuBalance} \n \n' f'Review transactions:\n{BoA.reviewTransactions}')
    driver.close()
    # startExpressVPN()

if __name__ == '__main__':
    SET_ACCOUNT_VARIABLE = "Personal" # Personal or Joint
    driver = Driver("Chrome")
    runBoA(driver, SET_ACCOUNT_VARIABLE)