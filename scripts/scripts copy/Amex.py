import os
import time
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Amex":
    from Functions.GeneralFunctions import (getPassword, getUsername, setDirectory, showMessage)
    from Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import (getPassword, getUsername, setDirectory, showMessage)
    from .Functions.GnuCashFunctions import (getGnuCashBalance, importGnuTransaction, openGnuCashBook)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl

def locateAmexWindow(driver):
    found = findWindowByUrl(driver, "global.americanexpress.com")
    if not found:
        amexLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1) 
        
def amexLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.americanexpress.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/header/div[2]/div[1]/div[3]/div/div[5]/ul/li[3]/span/a[1]").click()
    driver.find_element(By.ID, "eliloUserID").send_keys(getUsername(directory, 'Amex'))
    driver.find_element(By.ID, "eliloPassword").send_keys(getPassword(directory, 'Amex'))
    driver.find_element(By.ID, "loginSubmit").click()
    # handle pop-up
    try:
        driver.find_element(By.XPATH, "/html/body/div[1]/div[5]/div/div/div/div/div/div[2]/div/div/div/div/div[1]/div/a/span/span").click()
    except NoSuchElementException:
        exception = "caught"
    time.sleep(1)

def getAmexBalance(driver):
    locateAmexWindow(driver)
    return driver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[1]/div[1]/div/div[1]/div/div/span[1]/div").text.replace('$', '')

def exportAmexTransactions(driver):
    driver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[2]/div[2]/div/div[1]/div[1]/div/a").click()
    try: 
        # click on View Activity (for previous billing period)
        driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div[2]/div/div[2]/a/span").click()
    except NoSuchElementException:
        exception = "caught"
    # click on Download
    time.sleep(5)
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div[3]/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/div/table/thead/div/tr[1]/td[2]/div/div[2]/div/button").click()
    # click on CSV option
    driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/div/div/div/div[2]/div/div[1]/div/fieldset/div[2]/label").click()
    # delete old csv file, if present
    try:
        os.remove(r"C:\Users\dmagn\Downloads\activity.csv")
    except FileNotFoundError:
        exception = "caught"
    # click on Download
    driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/div/div/div/div/div[3]/a").click()
    time.sleep(3)

def claimAmexRewards(driver):
    locateAmexWindow(driver)   
    driver.get("https://global.americanexpress.com/rewards")
    rewardsBalance = driver.find_element(By.ID, "globalmrnavpointbalance").text.replace('$', '')
    if float(rewardsBalance) > 0:
        driver.find_element(By.ID, "rewardsInput").send_keys(rewardsBalance)
        driver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
        driver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()

def locateAndUpdateSpreadsheetForAmex(driver, amex):
    directory = setDirectory()
    # get current date
    today = datetime.today()
    month = today.month
    year = today.year
    # switch worksheets if running in December (to next year's worksheet)
    if month == 12:
        year = year + 1
    amexNeg = float(amex.strip('$')) * -1
    updateSpreadsheet(directory, 'Checking Balance', year, 'Amex', month, amexNeg, "Amex CC")
    updateSpreadsheet(directory, 'Checking Balance', year, 'Amex', month, amexNeg, "Amex CC", True)
    # Display Checking Balance spreadsheet
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=1688093622');")

def runAmex(driver):
    directory = setDirectory()
    locateAmexWindow(driver)
    amex = getAmexBalance(driver)
    exportAmexTransactions(driver)
    claimAmexRewards(driver)
    myBook = openGnuCashBook('Finance', False, False)
    reviewTrans = importGnuTransaction('Amex', r'C:\Users\dmagn\Downloads\activity.csv', myBook, driver, directory)
    amexGnu = getGnuCashBalance(myBook, 'Amex')
    locateAndUpdateSpreadsheetForAmex(driver, amex)
    if reviewTrans:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    showMessage("Balances + Review", f'Amex Balance: {amex} \n' f'GnuCash Amex Balance: {amexGnu} \n \n' f'Review transactions:\n{reviewTrans}')
    driver.quit()

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    runAmex(driver)
