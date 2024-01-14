import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__' or __name__ == "Fidelity":
    from Classes.Asset import USD, Security
    from Classes.GnuCash import GnuCash
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory)    
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory)    
    
def locateFidelityWindow(driver):
    found = driver.findWindowByUrl("digital.fidelity.com")
    if not found:
        fidelityLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def fidelityLogin(driver):
    driver.openNewWindow('https://digital.fidelity.com/prgw/digital/login/full-page')
    driver.webDriver.refresh()
    time.sleep(1)
    # driver.webDriver.find_element(By.ID,'password').send_keys(getPassword('Fidelity')) # pre-filled
    time.sleep(2)
    driver.webDriver.find_element(By.XPATH,"//*[@id='dom-login-button']/div").click() # login


def getFidelityIRABalance(driver):
    locateFidelityWindow(driver)
    return driver.webDriver.find_element(By.XPATH,"//*[@id='245173114']/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").text.replace('$','').replace(',','')

def getFidelityBrokerageBalance(driver):
    locateFidelityWindow(driver)
    return driver.webDriver.find_element(By.XPATH,"//*[@id='Z29380087']/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").text.replace('$','').replace(',','')    
                                                   
def getFidelityIRAPricesAndShares(driver, accounts, book):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-positions']/a/span").click() # Positions
    driver.clickElementOnceAvaiable("//*[@id='245173114']/span/s-slot/s-assigned-wrapper/div/div") # Roth IRA
    row = 1
    while True:
        row += 1
        try:
            symbol = driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[" + str(row) +"]/div/div/span/div/div[2]/div/button").text.replace('$','')
            print(symbol)
        except NoSuchElementException:
            break
        if symbol == 'VXUS':
            account = accounts['VXUS']
        elif symbol == 'VTI':
            account = accounts['VTI']
        elif symbol == 'Cash':
            account = accounts['SPAXX']
        else:
            continue

        if symbol != 'Cash':
            account.price = Decimal(driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[1]/div/span").text.replace('$', ''))
            book.updatePriceInGnucash(account.symbol, account.price)
            account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[9]/div/span").text.replace('$', '').replace(',',''))
            account.value = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',','')
        else:
            account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',',''))
    
def captureFidelityIRATransactions(driver):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-activity']/a/span").click() # Activity & Orders
    driver.clickElementOnceAvaiable("//*[@id='245173114']/span/s-slot/s-assigned-wrapper/div/div") # Roth IRA
    driver.webDriver.find_element(By.XPATH, "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/div/account-activity-container/div/div[1]/div[2]/pvd3-field-group/s-root/div/div/s-slot/s-assigned-wrapper/div/core-filter-button[2]/pvd3-button/s-root/button/div/span/s-slot/s-assigned-wrapper").click() # History
    driver.webDriver.find_element(By.XPATH, "//*[@id='timeperiod-select-button']/span[1]").click() # Timeframe
    driver.webDriver.find_element(By.XPATH, "//*[@id='60']/s-root/div/label").click() # past 60 days
    driver.webDriver.find_element(By.XPATH, "//*[@id='timeperiod-select-container']/div/div/pvd3-button/s-root/button").click() # Apply
    time.sleep(3)
    iraActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\ira.csv"
    open(iraActivity, 'w', newline='').truncate()
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    row = 2
    table = 2
    elementPath = "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/div/account-activity-container/div/div[3]/activity-list["          
    while True:
        row+=1
        column=1
        dateElement = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div['+str(row)+']/div/div['+str(column)+']')
        if dateElement.text == 'Load more results':
            break
        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date.month == lastMonth['endDate'].month:
            column+=1
            descriptionElement = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div['+str(row)+']/div/div['+str(column)+']/div/div')
            description = descriptionElement.text
            column+=1
            amount = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div['+str(row)+']/div/div['+str(column)+']').text.replace('$','').replace(',','').replace('-','').replace('+','')
            if not amount:
                continue
            if "YOU BOUGHT" in description.upper():
                descriptionElement.click()
                shares = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div['+str(row)+']/div[2]/div/activity-order-detail-panel/div/div/div[10]').text.replace('-','').replace('+','')
                descriptionElement.click()
            elif "CASH CONTRIBUTION" in description.upper():
                continue
            else:
                shares = amount
            transaction = date, description, amount, shares
            csv.writer(open(iraActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month > lastMonth['endDate'].month:
            continue
        else:
            break
    return iraActivity

def runFidelity(driver, accounts, book):
    locateFidelityWindow(driver)
    accounts['IRA'].setBalance(getFidelityIRABalance(driver))
    getFidelityIRAPricesAndShares(driver, accounts, book)
    iraActivity = captureFidelityIRATransactions(driver)
    book.importGnuTransaction(accounts['IRA'], iraActivity, driver, 0)
    accounts['VXUS'].updateGnuBalanceAndValue(book.getBalance(accounts['VXUS'].gnuAccount))
    accounts['VTI'].updateGnuBalanceAndValue(book.getBalance(accounts['VTI'].gnuAccount))
    accounts['SPAXX'].updateGnuBalanceAndValue(book.getBalance(accounts['SPAXX'].gnuAccount))
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    IRA = USD("IRA", book)
    VXUS = Security('Total Intl Stock Market', book)
    VTI = Security('Total Stock Market(IRA)', book)
    SPAXX = Security('Govt Money Market', book)
    Brokerage = USD("Brokerage", book)
    accounts = {'IRA': IRA,'VXUS': VXUS,'VTI': VTI,'SPAXX': SPAXX, 'Brokerage':Brokerage}
    runFidelity(driver, accounts, book)
    book.closeBook()
