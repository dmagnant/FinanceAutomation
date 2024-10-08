import time, os, json;    from datetime import datetime;  from decimal import Decimal
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Security;    from Classes.WebDriver import Driver;   from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getStartAndEndOfDateRange, getUsername, getNotes, setDirectory
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentsMonthly
    from Eternl import runEternl, locateEternlWindow
    from Ledger import runLedger, getLedgerAccounts
    from HealthEquity import runHealthEquity, locateHealthEquityWindow, getHealthEquityAccounts
    from IoPay import runIoPay, locateIoPayWindow
    from Worthy import runWorthy, locateWorthyWindow
    from Vanguard import runVanguard401k, locateVanguardWindow, getVanguardAccounts
    from Optum import runOptum, locateOptumWindow, getOptumAccounts
else:
    from .Classes.Asset import USD, Security;   from .Classes.WebDriver import Driver;  from .Classes.GnuCash import GnuCash
    from .Eternl import runEternl, locateEternlWindow
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import getStartAndEndOfDateRange, getUsername, getNotes, setDirectory
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentsMonthly
    from .HealthEquity import runHealthEquity, locateHealthEquityWindow, getHealthEquityAccounts
    from .IoPay import runIoPay, locateIoPayWindow
    from .Worthy import runWorthy, locateWorthyWindow
    from .Vanguard import runVanguard401k, locateVanguardWindow, getVanguardAccounts
    from .Optum import runOptum, locateOptumWindow, getOptumAccounts
    
def getMonthlyAccounts(type, personalBook, jointBook):
    if type == 'USD':
        HealthEquity = getHealthEquityAccounts(personalBook)
        Optum = getOptumAccounts(personalBook)
        Vanguard = getVanguardAccounts(personalBook)
        Savings = USD('Sofi Savings', personalBook)
        Worthy = USD("Worthy", personalBook)
        Pension = USD('Pension', personalBook)
        accounts = {'HealthEquity':HealthEquity,'Optum':Optum,'Vanguard':Vanguard,'Worthy': Worthy,'Savings': Savings, 'Pension': Pension}
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto", personalBook)
        Cardano = Security("Cardano", personalBook, 'ADA-Eternl')
        ledgerAccounts = getLedgerAccounts(personalBook)
        IoTex = Security("IoTex", personalBook)   
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Cardano': Cardano,'IoTex': IoTex, 'ledgerAccounts': ledgerAccounts}
    return accounts
    
def payWaterBill(driver, book):
    paymentAccountDetails = json.loads(getNotes('Ally Bank'))
    today = datetime.today()
    driver.openNewWindow('https://paywater.milwaukee.gov/webclient/user/login.seam')
    try:
        driver.webDriver.find_element(By.ID, 'login:j_id209:accountNumber').send_keys(getUsername('Water'))
        driver.webDriver.find_element(By.ID, 'login:submitAccountEnabled').click() # login
    except NoSuchElementException:  exception = "already logged in"
    driver.webDriver.find_element(By.ID, 'j_id172:j_id372').click() # make payment
    driver.findWindowByUrl('pay.bill2pay.com')
    driver.webDriver.find_element(By.ID,'txtUserField1').send_keys(os.environ.get('firstName') + " " + os.environ.get('lastName'))
    driver.webDriver.find_element(By.ID, 'txtPhone').send_keys(os.environ.get('Phone'))
    driver.webDriver.find_element(By.ID, 'btnSubmit').click() # Continue
    driver.webDriver.find_element(By.ID, 'txtNameonBankAccount').send_keys(os.environ.get('firstName') + " " + os.environ.get('lastName'))
    driver.webDriver.find_element(By.ID, 'ddlBankAccountType').send_keys(Keys.DOWN)
    driver.webDriver.find_element(By.ID, 'txtBankRoutingNumber').send_keys(paymentAccountDetails['routing'])
    driver.webDriver.find_element(By.ID, 'txtBankAccountNumber').send_keys(paymentAccountDetails['account'])
    driver.webDriver.find_element(By.ID, 'txtBankAccountNumber2').send_keys(paymentAccountDetails['account'])
    driver.webDriver.find_element(By.ID, 'btnSubmitAch').click() # Continue
    billTotal = driver.getXPATHElementTextOnceAvailable("//*[@id='tblAccountInfo']/tbody/tr[7]/td[2]").replace('$','')
    driver.webDriver.find_element(By.ID, 'txtEmailAddress').send_keys(os.environ.get('Email'))
    driver.webDriver.find_element(By.ID, 'chkTermsAgree').click() # agree to T&C
    driver.webDriver.find_element(By.ID, 'btnSubmit').click() # Make a Payment
    splits = [book.createSplit(round(Decimal(billTotal), 2), "Expenses:Utilities:Water"), book.createSplit(-round(Decimal(billTotal), 2), 'Ally')]
    book.writeTransaction(datetime.today().date(), 'Water Bill', splits)
    # splits=[Split(value=amount, account=self.getGnuAccount("Expenses:Utilities:Water")),
    #         Split(value=-amount, account=self.getGnuAccount("Assets:Ally Checking Account"))]
    # Transaction(post_date=datetime.today().date(), currency=book.currencies(mnemonic="USD"), description='Water Bill', splits=splits)
    # book.writeWaterBillTransaction(round(Decimal(billTotal), 2))
    updateSpreadsheet('Home', str(today.year) + ' Balance', 'Water Bill', today.month, -float(billTotal))
    openSpreadsheet(driver, 'Home', str(today.year) + ' Balance')
    driver.findWindowByUrl("/scripts/ally")
    
def loginToUSDAccounts(driver):
    locateWorthyWindow(driver)
    locateHealthEquityWindow(driver)
    locateVanguardWindow(driver)
    locateOptumWindow(driver)
 
def loginToCryptoAccounts(driver):
    locateEternlWindow(driver)
    locateIoPayWindow(driver)
    
def runUSD(driver, accounts, personalBook):
    loginToUSDAccounts(driver)
    lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    gnuCashTransactions = personalBook.getTransactionsByDateRange(lastMonth)
    runWorthy(driver, accounts['Worthy'], personalBook, gnuCashTransactions, lastMonth['endDate'])
    runHealthEquity(driver, accounts['HealthEquity'], personalBook, gnuCashTransactions, lastMonth)
    runOptum(driver, accounts['Optum'], personalBook, gnuCashTransactions, lastMonth)
    runVanguard401k(driver, accounts['Vanguard'], personalBook, gnuCashTransactions, lastMonth)
    accounts['Pension'].setCost(accounts['Pension'].gnuBalance - accounts['Pension'].getInterestTotalForDateRange(personalBook))
    accounts['Savings'].setCost(accounts['Savings'].gnuBalance - accounts['Savings'].getInterestTotalForDateRange(personalBook))
    updateInvestmentsMonthly(driver,personalBook,accounts)
    driver.findWindowByUrl("/scripts/monthly")

def runCrypto(driver, accounts, personalBook):
    loginToCryptoAccounts(driver)
    runEternl(driver, accounts['Cardano'], personalBook)
    runIoPay(driver, accounts['IoTex'], personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['CryptoPortfolio'].gnuAccount))
    driver.findWindowByUrl("/scripts/monthly")

def runMonthlyBank(personalBook, jointBook):
    driver = Driver("Chrome")
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)
    runUSD(driver, usdAccounts, personalBook)
    runCrypto(driver, cryptoAccounts, personalBook)

# if __name__ == '__main__': # USD
#     driver = Driver("Chrome")
#     today = datetime.today().date()
#     personalBook = GnuCash('Finance')
#     jointBook = GnuCash('Home')
#     usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
#     runUSD(driver, today, usdAccounts, personalBook)
#     personalBook.closeBook()
#     jointBook.closeBook()
    
# if __name__ == '__main__': # Crypto
#     driver = Driver("Chrome")
#     today = datetime.today().date()
#     personalBook = GnuCash('Finance')
#     jointBook = GnuCash('Home')
#     cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)    
#     runCrypto(driver, today, cryptoAccounts, personalBook)
#     personalBook.closeBook()
#     jointBook.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    # loginToUSDAccounts(driver)
    # import time, gspread
    # from datetime import datetime
    # worksheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Asset Allocation').worksheet('Investments')
    # symbol = worksheet.acell("B"+str(2)).value
    # print(symbol)
    # today = datetime.today().date()
    # personalBook = GnuCash('Finance')
    # jointBook = GnuCash('Home')
    # usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    # runUSD(driver, today, usdAccounts, personalBook)
    
    loginToUSDAccounts(driver)