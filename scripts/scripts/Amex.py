import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Amex":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, getUsername,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getPassword, getUsername,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import importGnuTransaction, openGnuCashUI

def locateAmexWindow(driver):
    found = driver.findWindowByUrl("global.americanexpress.com")
    if not found:
        amexLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
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
    return driver.webDriver.find_element(By.XPATH, "//*[@id='axp-balance-payment']/div[1]/div[1]/div/div[1]/div/div/span[1]/div").text.replace('$', '')

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
    driver.webDriver.get("https://global.americanexpress.com/rewards")
    rewardsBalance = driver.webDriver.find_element(By.ID, "globalmrnavpointbalance").text.replace('$', '')
    if float(rewardsBalance) > 0:
        driver.webDriver.find_element(By.ID, "rewardsInput").send_keys(rewardsBalance)
        driver.webDriver.find_element(By.XPATH, "//*[@id='continue-btn']/span").click()
        driver.webDriver.find_element(By.XPATH, "//*[@id='use-dollars-btn']/span").click()

def runAmex(driver):
    locateAmexWindow(driver)
    Amex = USD("Amex")
    Amex.setBalance(getAmexBalance(driver))
    exportAmexTransactions(driver.webDriver)
    claimAmexRewards(driver)
    importGnuTransaction(Amex, r'C:\Users\dmagn\Downloads\activity.csv', driver.webDriver)
    Amex.locateAndUpdateSpreadsheet(driver.webDriver)
    if Amex.reviewTransactions:
        openGnuCashUI('Finances')
    showMessage("Balances + Review", f'Amex Balance: {Amex.balance} \n' f'GnuCash Amex Balance: {Amex.gnuBalance} \n \n' f'Review transactions:\n{Amex.reviewTransactions}')
    driver.webDriver.close()

if __name__ == '__main__':
    driver = Driver("Chrome")
    runAmex(driver)