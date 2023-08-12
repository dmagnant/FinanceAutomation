import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
    driver.webDriver.find_element(By.ID,'fs-login-button').click() # login

def getFidelityBalance(driver):
    locateFidelityWindow(driver)
    return driver.webDriver.find_element(By.XPATH,"/html/body/ap143528-portsum-dashboard-root/dashboard-root/div/div[3]/accounts-selector/nav/div[2]/div[2]/div/pvd3-link/s-root/span/a/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").text.replace('$','').replace(',','')

def getFidelityPricesAndShares(driver, accounts, book):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-positions']/a/span").click() # Positions
    row = 1
    time.sleep(2)
    while True:
        row += 1
        try:
            symbol = driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[" + str(row) +"]/div/div/span/div/div[2]/div/button").text.replace('$','')
        except NoSuchElementException:
            break
        if symbol == 'VXUS':
            account = accounts['VXUS']
        elif symbol == 'VTI':
            account = accounts['VTI']
        elif symbol == 'SPAXX**':
            account = accounts['SPAXX']
        else:
            continue
        if symbol != 'SPAXX':
            account.price = Decimal(driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[1]/div/span").text.replace('$', ''))
            book.updatePriceInGnucash(account.symbol, account.price)
        account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[9]/div/span").text.replace('$', '').replace(',',''))
        account.value = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[2]/div/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',','')
        
def captureFidelityTransactions(driver):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-activity']/a/span").click() # Activity & Orders
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH, "//*[@id='timeperiod-select-button']/span[1]").click() # Timeframe
    driver.webDriver.find_element(By.XPATH, "//*[@id='60']/s-root/div/label").click() # past 60 days
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH, "//*[@id='timeperiod-select-container']/div/div/pvd3-button/s-root/button").click() # Apply
    driver.webDriver.find_element(By.XPATH, "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-panel/div/div/orders-grid-container/div/div[3]/activity-order-grid[2]/div/div[2]/activity-common-grid/div/pvd3-button/s-root/button/div/span/s-slot/s-assigned-wrapper").click()
    iraActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\ira.csv"
    open(iraActivity, 'w', newline='').truncate()
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    row = 0
    table = 1 if driver.webDriver.find_element(By.XPATH, "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-panel/div/div/orders-grid-container/div/div[3]/activity-order-grid[1]/div/div[1]").text != "Pending" else 2
    elementPath = "//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-panel/div/div/orders-grid-container/div/div[3]/activity-order-grid["
    while True:
        row+=1
        column=1
        date = datetime.strptime(driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div[2]/activity-common-grid/div/table/tbody['+str(row)+']/tr/td['+str(column)+']/div').text, '%b-%d-%Y').date()
        if date.month == lastMonth['endDate'].month:
            column+=1
            descriptionElement = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div[2]/activity-common-grid/div/table/tbody['+str(row)+']/tr/td['+str(column)+']/div')
            description = descriptionElement.text
            column+=2
            amount = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div[2]/activity-common-grid/div/table/tbody['+str(row)+']/tr/td['+str(column)+']/div[2]/span[1]').text.replace('$','').replace(',','').replace('-','').replace('+','')
            if "YOU BOUGHT" in description.upper():
                descriptionElement.click()
                shares = driver.webDriver.find_element(By.XPATH,elementPath+str(table)+']/div/div[2]/activity-common-grid/div/table/tbody['+str(row)+']/tr[2]/td/activity-order-detail-panel/div/div/div[10]').text.replace('-','').replace('+','')
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
    accounts['Fidelity'].setBalance(getFidelityBalance(driver))
    getFidelityPricesAndShares(driver, accounts, book)
    iraActivity = captureFidelityTransactions(driver)
    book.importGnuTransaction(accounts['Fidelity'], iraActivity, driver, 0)
    accounts['VXUS'].updateGnuBalanceAndValue(book.getBalance(accounts['VXUS'].gnuAccount))
    accounts['VTI'].updateGnuBalanceAndValue(book.getBalance(accounts['VTI'].gnuAccount))
    print(accounts['VTI'].balance)
    accounts['SPAXX'].updateGnuBalanceAndValue(book.getBalance(accounts['SPAXX'].gnuAccount))
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Fidelity = USD("Fidelity", book)
    VXUS = Security('Total Intl Stock Market', book)
    VTI = Security('Total Stock Market(IRA)', book)
    SPAXX = Security('Govt Money Market', book)
    accounts = {'Fidelity': Fidelity,'VXUS': VXUS,'VTI': VTI,'SPAXX': SPAXX}
    runFidelity(driver, accounts, book)