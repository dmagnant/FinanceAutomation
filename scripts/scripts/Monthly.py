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
    from HealthEquity import runHealthEquity, locateHealthEquityWindow
    from IoPay import runIoPay, locateIoPayWindow
    from Worthy import getWorthyBalance, locateWorthyWindow
    from Vanguard import runVanguard401k, locateVanguardWindow
    from Fidelity import runFidelity, locateFidelityWindow
    from Optum import runOptum, locateOptumWindow
else:
    from .Classes.Asset import USD, Security;   from .Classes.WebDriver import Driver;  from .Classes.GnuCash import GnuCash
    from .Eternl import runEternl, locateEternlWindow
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import getStartAndEndOfDateRange, getUsername, getNotes, setDirectory
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentsMonthly
    from .HealthEquity import runHealthEquity, locateHealthEquityWindow
    from .IoPay import runIoPay, locateIoPayWindow
    from .Worthy import getWorthyBalance, locateWorthyWindow
    from .Vanguard import runVanguard401k, locateVanguardWindow
    from .Fidelity import runFidelity, locateFidelityWindow
    from .Optum import runOptum, locateOptumWindow
    
def getMonthlyAccounts(type, personalBook, jointBook):
    if type == 'USD':
        IRA, iraSPAXX, iraGME = USD("IRA", personalBook), Security('IRA SPAXX', personalBook), Security('IRA GME', personalBook)
        rIRA, riraVXUS, riraVTI, riraSPAXX, riraGME = USD("Roth IRA", personalBook), Security('Roth IRA VXUS', personalBook), Security('Roth IRA VTI', personalBook), Security('Roth IRA SPAXX', personalBook), Security('Roth IRA GME', personalBook)
        Brokerage, brSPAXX, brGME = USD("Brokerage", personalBook), Security('Brokerage SPAXX', personalBook), Security('Brokerage GME', personalBook)
        VIIIX, HECash = Security("HE Investment", personalBook), USD("HE Cash", personalBook)
        VFIAX, OptumCash = Security("VFIAX", personalBook), USD("Optum Cash", personalBook)
        V401k, TSM401k, EBI = USD("Vanguard401k", personalBook), Security("Total Stock Market(401k)", personalBook), Security("Employee Benefit Index", personalBook)
        LiquidAssets = USD("Liquid Assets", personalBook)
        Bonds, Worthy = USD("Bonds", personalBook), USD("Worthy", personalBook)        
        accounts = {'IRA':IRA,'iraSPAXX':iraSPAXX,'iraGME':iraGME,'rIRA':rIRA,'riraVXUS':riraVXUS,'riraVTI':riraVTI,'riraSPAXX':riraSPAXX,'riraGME':riraGME,'Brokerage':Brokerage,'brSPAXX':brSPAXX, 'brGME':brGME,
                    'VIIIX':VIIIX,'HECash':HECash,'VFIAX':VFIAX,'OptumCash':OptumCash,'V401k':V401k,'EBI':EBI,'TSM401k':TSM401k,'Worthy': Worthy,'LiquidAssets':LiquidAssets,'Bonds':Bonds}
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto", personalBook)
        Cardano = Security("Cardano", personalBook, 'ADA-Eternl')
        ledgerAccounts = getLedgerAccounts(personalBook)
        IoTex = Security("IoTex", personalBook)   
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Cardano': Cardano,'IoTex': IoTex, 'ledgerAccounts': ledgerAccounts}
    return accounts

def monthlyRoundUp(account, myBook, date):
    change = round(Decimal(account.balance - float(account.gnuBalance)), 2)
    # change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":    transactionVariables = {'postDate': date, 'description': "Interest", 'amount': -change, 'fromAccount': "Income:Investments:Interest"}
    myBook.writeGnuTransaction(transactionVariables, account.gnuAccount)
    account.updateGnuBalance(myBook.getGnuAccountBalance(account.gnuAccount))
    
def updateEnergyBillAmounts(driver, book, amount):
    driver.openNewWindow('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx')
    time.sleep(2)
    try:
        # driver.webDriver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername('WE-Energies (Home)'))
        # driver.webDriver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword('WE-Energies (Home)'))
        driver.webDriver.find_element(By.XPATH, "//*[@id='next']").click() # login
        time.sleep(4)
        driver.webDriver.find_element(By.XPATH, "//*[@id='notInterested']/a").click # close out of app notice
    except NoSuchElementException:  exception = "caught"
    driver.webDriver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click() # view bill history
    time.sleep(4)
    billRow, billColumn, billNotFound = 2, 7, True
    while billNotFound:
        weBillAmount = driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span").text.replace('$', '')
        if amount == weBillAmount:  billNotFound = False
        else:   billRow += 1
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gas = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricity = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    book.writeUtilityTransaction({'electricity': electricity, 'gas': gas, 'total': amount})
    print(f'posted transaction: \n' f'date: {str(datetime.today().date())} \n' f'total: {str(amount)} \n' f'electricity: {str(electricity)}\n' f'gas: {str(gas)}')
    today = datetime.today()
    updateSpreadsheet('Home', str(today.year) + ' Balance', 'Energy Bill', today.month, -float(amount))
    openSpreadsheet(driver, 'Home', str(today.year) + ' Balance')
    driver.findWindowByUrl("/scripts/ally")
    
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
    book.writeWaterBillTransaction(round(Decimal(billTotal), 2))
    updateSpreadsheet('Home', str(today.year) + ' Balance', 'Water Bill', today.month, -float(billTotal))
    openSpreadsheet(driver, 'Home', str(today.year) + ' Balance')
    driver.findWindowByUrl("/scripts/ally")
    
def loginToUSDAccounts(driver):
    locateWorthyWindow(driver)
    locateHealthEquityWindow(driver)
    locateVanguardWindow(driver)
    locateFidelityWindow(driver)
    locateOptumWindow(driver)
 
def loginToCryptoAccounts(driver):
    locateEternlWindow(driver)
    locateIoPayWindow(driver)
    
def runUSD(driver, today, accounts, personalBook):
    loginToUSDAccounts(driver)
    lastMonth = getStartAndEndOfDateRange(today, "month")
    getWorthyBalance(driver, accounts['Worthy'])
    monthlyRoundUp(accounts['Worthy'], personalBook, lastMonth['endDate'])
    runHealthEquity(driver, {'VIIIX': accounts['VIIIX'], 'HECash': accounts['HECash'],'V401k': accounts['V401k']}, personalBook)
    runOptum(driver, accounts, personalBook)
    accounts['LiquidAssets'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['LiquidAssets'].gnuAccount))
    accounts['Bonds'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['Bonds'].gnuAccount))
    runVanguard401k(driver, accounts, personalBook)
    runFidelity(driver, accounts, personalBook)
    updateInvestmentsMonthly(driver,personalBook,accounts)
    driver.findWindowByUrl("/scripts/monthly")

def runCrypto(driver, accounts, personalBook):
    loginToCryptoAccounts(driver)
    runEternl(driver, accounts['Cardano'], personalBook)
    runIoPay(driver, accounts['IoTex'], personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['CryptoPortfolio'].gnuAccount))
    driver.findWindowByUrl("/scripts/monthly")

def runMonthlyBank(personalBook, jointBook):
    today = datetime.today().date()
    driver = Driver("Chrome")
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)
    runUSD(driver, today, usdAccounts, personalBook)
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