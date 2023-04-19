import time
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Vanguard":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, showMessage)
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange,
                                             getUsername, showMessage)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
    
def getVanguardPrices(driver):
    locateVanguardWindow(driver)
    driver.openNewWindow('https://retirementplans.vanguard.com/VGApp/pe/faces/Investments.xhtml?SelectedPlanId=095895')
    price8188 = 0
    price8585 = 0
    num = 2
    while price8188 == 0 or price8585 == 0:
        fundNumber = driver.webDriver.find_element(By.XPATH, '/html/body/div[2]/div[7]/span[2]/form/div[2]/div/div/div[2]/div/div/span[1]/div/span/span[1]/table/tbody/tr[' + str(num) + ']/td[1]').text
        price = driver.webDriver.find_element(By.XPATH, '/html/body/div[2]/div[7]/span[2]/form/div[2]/div/div/div[2]/div/div/span[1]/div/span/span[1]/table/tbody/tr[' + str(num) + ']/td[4]').text.replace('$', '')
        if fundNumber == str(8188):
            price8188 = price
        elif fundNumber == str(8585):
            price8585 = price
        num+=1
    return {'8188': price8188, '8585': price8585}
    
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
    driver.find_element(By.ID, "username").send_keys(getUsername('Vanguard'))
    time.sleep(1)
    driver.find_element(By.ID, "pword").send_keys(getPassword('Vanguard'))
    time.sleep(1)
    driver.find_element(By.XPATH, "//*[@id='vui-button-1']/button/div").click() # log in 
    try:     # handle security code
        driver.find_element(By.ID, 'CODE')
        showMessage('Security Code', "Enter Security code, then click OK")
        driver.find_element(By.XPATH,"//*[@id='radioGroupId-bind-selection-group']/c11n-radio[1]/label/div").click() # remember me
        driver.find_element(By.XPATH, "//*[@id='security-code-submit-btn']/button/span/span").click() # verify
    except NoSuchElementException:
        exception = "caught"

def getVanguardBalanceAndInterestYTD(driver, accounts):
    locateVanguardWindow(driver)    
    driver.webDriver.get('https://ownyourfuture.vanguard.com/main/dashboard/assets-details')
    time.sleep(2)
    pensionBalance = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[3]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    v401kBalance = driver.webDriver.find_element(By.XPATH,"/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')                                                  
    accounts[0].setBalance(pensionBalance)
    accounts[1].setBalance(v401kBalance)
    interestYTD = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[4]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    return interestYTD

def importGnuTransactions(book, today, account, interestYTD):
    lastMonth = getStartAndEndOfDateRange(today, "month")
    interestAmount = 0
    transactions = [tr for tr in book.readBook.transactions
                    if str(tr.post_date.strftime('%Y')) == str(lastMonth['startDate'].year)
                    for spl in tr.splits
                    if spl.account.fullname == account.gnuAccount]
    for tr in transactions:
        for spl in tr.splits:
            if spl.account.fullname == "Income:Investments:Interest":
                interestAmount = interestAmount + abs(spl.value)
    accountChange = Decimal(account.balance) - account.gnuBalance
    interest = Decimal(interestYTD) - interestAmount
    employerContribution = accountChange - interest
    amount = {'interest': -interest, 'employerContribution': -employerContribution, 'accountChange': accountChange}
    transactionVariables = {'postDate': lastMonth['endDate'], 'description': "Contribution + Interest", 'amount': amount, 'fromAccount': account.gnuAccount}
    # writeGnuTransaction(myBook, "Contribution + Interest", lastMonth.endDate, [-interest, -employerContribution, accountChange], account.gnuAccount)
    book.writeGnuTransaction(transactionVariables)
    return {"interest": interest, "employerContribution": employerContribution}
    
def runVanguard(driver, accounts, book):
    today = datetime.today().date()
    locateVanguardWindow(driver)
    interestYTD = getVanguardBalanceAndInterestYTD(driver, accounts)
    pensionInfo = importGnuTransactions(book, today, accounts[0], interestYTD)
    accounts[0].updateGnuBalance(book.getBalance(accounts[0].gnuAccount))

    openSpreadsheet(driver, 'Asset Allocation', '2022')
    updateSpreadsheet('Asset Allocation', today.year, 'VanguardPension', today.month, float(accounts[0].balance))
    book.openGnuCashUI()
    return pensionInfo

if __name__ == '__main__':
    # driver = Driver("Chrome")
    # book = GnuCash('Finance')
    # Pension = USD("VanguardPension", book)
    # V401k = USD("Vanguard401k", book)
    # accounts = [Pension, V401k]
    # pensionInfo = runVanguard(driver, accounts, book)
    # for a in accounts:
    #     a.getData()
    # print('  Interested Earned: ' + str(pensionInfo.interest))
    # print('total contributions: ' + str(pensionInfo.employerContributions))
    # book.closeBook()


    driver = Driver("Chrome")
    object = getVanguardPrices(driver)
    print(object)