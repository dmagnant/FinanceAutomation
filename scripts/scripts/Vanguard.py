import time, csv
from datetime import datetime
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Vanguard":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, showMessage, setDirectory)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange,
                                             getUsername, showMessage, setDirectory)

def vanguardLogin(driver):
    driver.openNewWindow('https://logon.vanguard.com/logon?site=pi')
    driver = driver.webDriver
    # driver.find_element(By.ID, "USER").send_keys(getUsername('Vanguard'))
    time.sleep(1)
    # driver.find_element(By.ID, "PASSWORD-blocked").send_keys(getPassword('Vanguard'))
    time.sleep(1)
    driver.find_element(By.XPATH, "//*[@id='username-password-submit-btn-1']/span").click() # log in 
    try:     # handle security code
        driver.find_element(By.ID, 'CODE')
        showMessage('Security Code', "Enter Security code, then click OK")
        driver.find_element(By.XPATH,"//*[@id='radioGroupId-bind-selection-group']/c11n-radio[1]/label/div").click() # remember me
        driver.find_element(By.XPATH, "//*[@id='security-code-submit-btn']/button/span/span").click() # verify
    except NoSuchElementException:
        exception = "caught"
    driver.get('https://ownyourfuture.vanguard.com/main/dashboard')

def locateVanguardWindow(driver):
    found = driver.findWindowByUrl("ownyourfuture.vanguard.com/main")
    if not found:
        vanguardLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
    
def getVanguard401kPriceAndShares(driver, accounts, book):
    locateVanguardWindow(driver)
    driver.openNewWindow('https://retirementplans.vanguard.com/VGApp/pe/faces/Investments.xhtml?SelectedPlanId=095895')
    num = 2
    while num <=3:
        fundNumber = driver.webDriver.find_element(By.XPATH, "//*[@id='investmentsForm:allFundsTabletbody0']/tr[" + str(num) + "]/td[1]").text        
        account = accounts['TSM401k'] if fundNumber == str(8585) else accounts['REIF401k']
        account.balance = driver.webDriver.find_element(By.XPATH, "//*[@id='investmentsForm:allFundsTabletbody0']/tr[" + str(num) + "]/td[3]").text
        account.price = driver.webDriver.find_element(By.XPATH, "//*[@id='investmentsForm:allFundsTabletbody0']/tr[" + str(num) + "]/td[4]").text.replace('$', '')
        book.updatePriceInGnucash(account.symbol, Decimal(account.price))
        account.value = driver.webDriver.find_element(By.XPATH,"//*[@id='investmentsForm:allFundsTabletbody0']/tr[" + str(num) + "]/td[5]").text.replace('$','',).replace(',','')
        num+=1
    accounts['V401k'].balance = driver.webDriver.find_element(By.XPATH, "//*[@id='investmentsForm:allFundsTabletbody0']/tr[" + str(num) + "]/td[5]").text.replace("$", "").replace(',', '')
    
def captureVanguard401kTransactions(driver):
    locateVanguardWindow(driver)
    driver.openNewWindow('https://retirementplans.vanguard.com/VGApp/pe/faces/TransactionHistory.xhtml?SelectedPlanId=095895')
    lastMonth = getStartAndEndOfDateRange(datetime.today().date(), "month")
    v401kActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\401k.csv"
    open(v401kActivity, 'w', newline='').truncate()
    driver.webDriver.find_element(By.ID,"TransactionHistoryTabBox:transHistoryForm:viewByDate_main").click() # View history from: option
    driver.webDriver.find_element(By.ID,"TransactionHistoryTabBox:transHistoryForm:viewByDate:historyItemLabel2").click() # View last 3 months to ensure all transactions are visible
    time.sleep(1)
    row = 1
    transactionTable = "//*[@id='TransactionHistoryTabBox:transHistoryForm:transactionHistoryDataTabletbody0']/tr["
    while True:
        column=1
        row+=1
        date = datetime.strptime(driver.webDriver.find_element(By.XPATH,(transactionTable + str(row) + "]/td[" + str(column) + "]")).text, '%m/%d/%Y').date()
        description = ''
        if date.month == lastMonth['endDate'].month:
            column+=1
            description = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text
            column+=1
            description +=" "+ driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text
            column+=1
            shares = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text
            column+=2
            amount = driver.webDriver.find_element(By.XPATH,transactionTable + str(row) + "]/td[" + str(column) + "]").text.replace('$','')
            amount = -float(amount) if "Fee" in description else amount
            shares = -float(shares) if "Fee" in description else shares
            transaction = date, description, shares, amount
            csv.writer(open(v401kActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month < lastMonth['endDate'].month or date.year < lastMonth['endDate'].year:
            break
    return v401kActivity
    
def getVanguardBalancesAndPensionInterestYTD(driver, accounts):
    locateVanguardWindow(driver)
    driver.openNewWindow('https://ownyourfuture.vanguard.com/main/dashboard/assets-details')
    time.sleep(2)
    pensionBalance = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[3]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    v401kBalance = driver.webDriver.find_element(By.XPATH,"/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')                                                  
    accounts['Pension'].setBalance(pensionBalance)
    accounts['V401k'].setBalance(v401kBalance)
    interestYTD = driver.webDriver.find_element(By.XPATH, "/html/body/div[3]/div/app-personalized-dashboard-root/app-assets-details/app-balance-details/div/div[3]/div[4]/div/app-details-card/div/div/div[1]/div[3]/h4").text.strip('$').replace(',', '')
    return interestYTD

def calculatePensionTransactions(book, today, account, interestYTD):
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
    return {'postDate': lastMonth['endDate'], 'description': "Contribution + Interest", 'amount': amount, 'fromAccount': account.gnuAccount}
    
def runVanguard401k(driver, accounts, book):
    locateVanguardWindow(driver)
    getVanguard401kPriceAndShares(driver, accounts, book)
    v401kActivity = captureVanguard401kTransactions(driver)
    book.importGnuTransaction(accounts['V401k'], v401kActivity, driver, 0)
    accounts['REIF401k'].updateGnuBalanceAndValue(book.getBalance(accounts['REIF401k'].gnuAccount))
    accounts['TSM401k'].updateGnuBalanceAndValue(book.getBalance(accounts['TSM401k'].gnuAccount))
    accounts['V401k'].updateGnuBalance(book.getBalance(accounts['V401k'].gnuAccount))
    
def runVanguardPension(driver, accounts, book):
    today = datetime.today().date()
    locateVanguardWindow(driver)
    interestYTD = getVanguardBalancesAndPensionInterestYTD(driver, accounts)
    book.writeGnuTransaction(calculatePensionTransactions(book, today, accounts['Pension'], interestYTD))
    accounts['Pension'].updateGnuBalance(book.getBalance(accounts['Pension'].gnuAccount))

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Pension = USD("VanguardPension", book)
    V401k = USD("Vanguard401k", book)
    REIF401k = Security("Real Estate Index Fund", book)
    TSM401k = Security("Total Stock Market(401k)", book)
    accounts = {'Pension': Pension, 'V401k': V401k, 'REIF401k': REIF401k, 'TSM401k': TSM401k}
    # runVanguard401k(driver, accounts, book)
    runVanguardPension(driver,accounts,book)
    Pension.getData()
    V401k.getData()
    book.closeBook()
    
    # REIF401k = Security("Real Estate Index Fund", book)
    # TSM401k = Security("Total Stock Market(401k)", book)
    # print(REIF401k.gnuValue)
    # print(TSM401k.gnuValue)
    
    # REIF401k.updateGnuBalanceAndValue(book.getBalance(REIF401k.gnuAccount))
    # print(REIF401k.gnuValue)


    # price = book.getPriceInGnucash(accounts['TSM401k'].symbol)
    # print(price)
    
    # book.updatePriceInGnucash(accounts['TSM401k'].symbol, round(Decimal(118.30), 2))
    # today = datetime.today().date()
    # price1 = book.getPriceInGnucash(accounts['TSM401k'].symbol, today)
    # print(price1)