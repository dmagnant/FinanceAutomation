import time
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "HealthEquity":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage)    
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage)    
    
def locateHealthEquityWindow(driver):
    found = driver.findWindowByUrl("member.my.healthequity.com")
    if not found:
        healthEquitylogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def healthEquitylogin(driver):
    driver.openNewWindow('https://member.my.healthequity.com/hsa/21895515-010')
    driver = driver.webDriver
    try:
        driver.find_element(By.ID, "ctl00_modulePageContent_btnLogin").click() # login
        try:  # Two-Step Authentication
            driver.find_element(By.XPATH, "//*[@id='sendEmailTextVoicePanel']/div[5]/span[1]/span/label/span/strong").click() # send code to phone
            driver.find_element(By.ID, "sendOtp").click() # Send confirmation code
            showMessage("Confirmation Code", "Enter code then click OK") # enter text code
            driver.find_element(By.XPATH, "//*[@id='VerifyOtpPanel']/div[4]/div[1]/div/label/span").click() # Remember me
            driver.find_element(By.ID, "verifyOtp").click() # click Confirm
        except NoSuchElementException:
            exception = "already verified"
    except NoSuchElementException:
        exception = "already logged in"
    time.sleep(1)

def getHealthEquityBalances(driver, accounts):
    locateHealthEquityWindow(driver)
    driver = driver.webDriver
    HE_hsa_avail_bal = driver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/div/span[1]").text.strip('$').replace(',','')
    HE_hsa_invest_bal = driver.find_element(By.XPATH, "//*[@id='21895515-020']/div/hqy-hsa-tab/div/div[2]/span[2]/span[1]").text.strip('$').replace(',','')
    accounts['HealthEquity'].setBalance(float(HE_hsa_avail_bal) + float(HE_hsa_invest_bal))
    vanguard401kbalance = driver.find_element(By.XPATH, "//*[@id='retirementAccounts']/li/a/div/ul/li/span[2]").text.strip('$').replace(',','')
    accounts['Vanguard'].setBalance(float(vanguard401kbalance))

def getHealthEquityDividends(driver):
    lastMonth = getStartAndEndOfDateRange(datetime.today(), "month")
    driver = driver.webDriver
    driver.find_element(By.XPATH, "//*[@id='hsaInvestment']/div/div/a").click() # Manage HSA Investments
    time.sleep(1)
    driver.find_element(By.ID, "EditPortfolioTab").click() # Portfolio performance
    time.sleep(4)
    num = 0
    while num < 10:     # enter Start Date and End Date
        driver.find_element(By.ID, "startDate").click()
        driver.find_element(By.ID, "startDate").send_keys(Keys.BACKSPACE)
        driver.find_element(By.ID, "endDate").click()
        driver.find_element(By.ID, "endDate").send_keys(Keys.BACKSPACE)  
        num += 1
    driver.find_element(By.ID, "startDate").send_keys(datetime.strftime(lastMonth[0], '%m/%d/%Y'))
    driver.find_element(By.ID, "endDate").send_keys(datetime.strftime(lastMonth[1], '%m/%d/%Y'))
    driver.find_element(By.ID, "fundPerformanceRefresh").click() # Refresh
    time.sleep(1)
    return Decimal(driver.find_element(By.XPATH, "//*[@id='EditPortfolioTab-panel']/member-portfolio-edit-display/member-overall-portfolio-performance-display/div[1]/div/div[3]/div/span").text.strip('$').strip(','))

def runHealthEquity(driver, accounts):
    locateHealthEquityWindow(driver)
    getHealthEquityBalances(driver, accounts)
    return getHealthEquityDividends(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    HealthEquity = USD("HSA")
    Vanguard = USD("Vanguard401k")
    HEaccounts = {
        'HealthEquity': HealthEquity, 
        'Vanguard': Vanguard
    }
    HSA_dividends = runHealthEquity(driver, HEaccounts)
    HealthEquity.getData()
    Vanguard.getData()
    print("HSA Dividends: " + str(HSA_dividends))
    