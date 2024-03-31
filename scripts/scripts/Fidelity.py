import time, csv, json
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
    from Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes)    
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (showMessage, getPassword, getStartAndEndOfDateRange, setDirectory, getNotes)    
    
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

def getFidelityBalance(driver, allAccounts, accountBalanceToGet='all'):
    locateFidelityWindow(driver)
    accountsToUpdate = ['Brokerage', 'IRA', 'rIRA'] if accountBalanceToGet == 'all' else [accountBalanceToGet]
    accountNums = json.loads(getNotes('Fidelity'))
    for account in accountsToUpdate:
        accountNum = str(accountNums[account])
        balance = driver.getXPATHElementTextOnceAvailable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").replace('$','').replace(',','')
        allAccounts[account].setBalance(balance)

def getFidelityPricesAndShares(driver, allAccounts, book, accountToGet='all'):
    locateFidelityWindow(driver)
    accountNum = str(json.loads(getNotes('Fidelity'))[accountToGet]) if accountToGet != 'all' else 'allaccounts'
    driver.clickXPATHElementOnceAvaiable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div") # Account
    driver.clickXPATHElementOnceAvaiable("//*[@id='portsum-tab-positions']/a/span") # Positions
    driver.webDriver.implicitly_wait(1)
    row = 0
    while True:
        row += 1
        try:
            accountName = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/h3").text
            if 'Traditional' in accountName:
                row+=2
        except NoSuchElementException:
            try:
                symbol = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/div/button").text.replace('$','')
                if symbol == 'VXUS':
                    if 'ROTH' in accountName:
                        account = allAccounts['riraVXUS']
                elif symbol == 'VTI':
                    if 'ROTH' in accountName:            
                        account = allAccounts['riraVTI']
                elif symbol == 'Cash':
                    if 'ROTH' in accountName:
                        account = allAccounts['riraSPAXX']
                    elif 'Individual' in accountName:
                        account = allAccounts['brSPAXX']
                    elif 'Traditional' in accountName:
                        account = allAccounts['iraSPAXX']
                else:
                    continue

                if symbol != 'Cash':
                    account.price = Decimal(driver.webDriver.find_element(By.XPATH, "//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[1]/div/span").text.replace('$', ''))
                    book.updatePriceInGnucash(account.symbol, account.price)
                    account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[9]/div/span").text.replace('$', '').replace(',',''))
                    account.value = driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',','')
                else:
                    account.setBalance(driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[" + str(row) + "]/div[7]/div/span").text.replace('$', '').replace(',',''))
            except NoSuchElementException:
                if accountToGet != 'all':
                    if row==2:
                        showMessage('Failed to Find Individual Account Share/Price Info', 'Need to update element information for prices and shares in Fidelity')
                    break
                try:
                    if 'Account Total' == driver.webDriver.find_element(By.XPATH,"//*[@id='posweb-grid']/div/div[2]/div[2]/div[3]/div[1]/div[1]/div["+ str(row) +"]/div/div/span/div/div[2]/div/p").text:
                        row+=1
                except NoSuchElementException:
                    if row==1:
                        showMessage('Failed to Find Share Info', 'Need to update element information for prices and shares in Fidelity')
                    break

def captureFidelityTransactions(driver, account='all'):
    locateFidelityWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='portsum-tab-activity']/a/span").click() # Activity & Orders
    accountNum = str(json.loads(getNotes('Fidelity'))[account]) if account != 'all' else 'allaccounts'
    driver.clickXPATHElementOnceAvaiable(f"//*[@id='{accountNum}']/span/s-slot/s-assigned-wrapper/div/div") # Account
    driver.clickXPATHElementOnceAvaiable("//*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[1]/div[2]/apex-kit-field-group/s-root/div/div/s-slot/s-assigned-wrapper/div/core-filter-button[2]/pvd3-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # History
    driver.clickXPATHElementOnceAvaiable("//*[@id='timeperiod-select-button']/span[1]") #Timeframe
    driver.clickXPATHElementOnceAvaiable("//*[@id='60']/s-root/div/label") # past 60 days
    driver.clickXPATHElementOnceAvaiable("//*[@id='timeperiod-select-container']/div/div/apex-kit-button/s-root/button/div/span/s-slot/s-assigned-wrapper") # Apply
    time.sleep(1)
    fidelityActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\fidelity.csv"
    open(fidelityActivity, 'w', newline='').truncate()
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    row = 0
    table = 3
    elementPathRoot = " //*[@id='accountDetails']/div/div[2]/div/new-tab-group/new-tab-group-ui/div[2]/activity-orders-shell/div/ap143528-portsum-dashboard-activity-orders-home-root/div/div/account-activity-container/div/div[2]/activity-list[2]/div/div["
    
    def setElementPath(eRow, eTable, eColumn):
        return elementPathRoot + str(eTable)+']/div['+str(eRow)+']/div/div['+str(eColumn) + ']'
    
    while True:
        row+=1
        column=2
        accountName = account
        try:
            dateElement = driver.webDriver.find_element(By.XPATH,setElementPath(row, table, column))
        except NoSuchElementException:
            if row==1:
                showMessage('Error finding Date Element', 'Element path for date element has changed, please update.')
            break
        date = datetime.strptime(dateElement.text, '%b-%d-%Y').date()
        if date.month == lastMonth['endDate'].month:
            column+=1
            if account == 'all':
                accountName = driver.webDriver.find_element(By.XPATH,setElementPath(row, table, column)).text
                if 'ROTH' in accountName:
                    accountName = 'rIRA'
                elif 'Individual' in accountName:
                    accountName = 'Brokerage'
                elif 'Traditional' in accountName:
                    accountName = 'IRA'
                column+=1
            descriptionElement = driver.webDriver.find_element(By.XPATH,setElementPath(row, table, column)+'/div')
            description = descriptionElement.text
            column+=1
            amount = driver.webDriver.find_element(By.XPATH,setElementPath(row, table, column)).text.replace('$','').replace(',','').replace('-','').replace('+','')
            if not amount:
                continue
            if "YOU BOUGHT" in description.upper():
                descriptionElement.click()
                shares = driver.webDriver.find_element(By.XPATH,elementPathRoot+str(table)+']/div/div['+str(row)+']/div[2]/div/activity-order-detail-panel/div/div/div[10]').text.replace('-','').replace('+','')
                descriptionElement.click()
            elif "CASH CONTRIBUTION" in description.upper() or "ELECTRONIC FUNDS TRANSFER" in description.upper() or "REINVESTMENT" in description.upper() or "LIQUIDATION" in description.upper():
                continue
            else:
                shares = amount
            transaction = date, description, amount, shares, accountName
            csv.writer(open(fidelityActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month < lastMonth['endDate'].month or date.year < lastMonth['endDate'].year:
            break
    return fidelityActivity

def runFidelity(driver, accounts, book):
    locateFidelityWindow(driver)
    getFidelityBalance(driver, accounts)
    getFidelityPricesAndShares(driver, accounts, book)
    fidelityActivity = captureFidelityTransactions(driver)
    book.importGnuTransaction(accounts, fidelityActivity, driver, 0)
    accounts['riraVXUS'].updateGnuBalanceAndValue(book.getBalance(accounts['riraVXUS'].gnuAccount))
    accounts['riraVTI'].updateGnuBalanceAndValue(book.getBalance(accounts['riraVTI'].gnuAccount))
    accounts['riraSPAXX'].updateGnuBalanceAndValue(book.getBalance(accounts['riraSPAXX'].gnuAccount))
    accounts['iraSPAXX'].updateGnuBalanceAndValue(book.getBalance(accounts['iraSPAXX'].gnuAccount))
    accounts['brSPAXX'].updateGnuBalanceAndValue(book.getBalance(accounts['brSPAXX'].gnuAccount))
    
def getFidelityAccounts(book):
    IRA = USD("IRA", book)
    iraSPAXX = Security('IRA SPAXX', book)
    rIRA = USD("Roth IRA", book)
    riraVXUS = Security('Roth IRA VXUS', book)
    riraVTI = Security('Roth IRA VTI', book)
    riraSPAXX = Security('Roth IRA SPAXX', book)
    Brokerage = USD("Brokerage", book)
    brSPAXX = brSPAXX = Security('Brokerage SPAXX', book)
    return {'rIRA': rIRA,'riraVXUS': riraVXUS,'riraVTI': riraVTI,'riraSPAXX': riraSPAXX, 'Brokerage':Brokerage, 'brSPAXX':brSPAXX, 'IRA':IRA, 'iraSPAXX':iraSPAXX}
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    accounts = getFidelityAccounts(book)
    runFidelity(driver, accounts, book)
    book.closeBook()
