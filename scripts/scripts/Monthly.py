import time;    from datetime import datetime;  from decimal import Decimal
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Security;    from Classes.WebDriver import Driver;   from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getStartAndEndOfDateRange
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPricesAndShares
    from Eternl import runEternl
    from Ledger import runLedger, getLedgerAccounts
    from HealthEquity import runHealthEquity
    from IoPay import runIoPay
    from Worthy import getWorthyBalance 
    from Vanguard import runVanguard401k
    from Fidelity import runFidelity
else:
    from .Classes.Asset import USD, Security;   from .Classes.WebDriver import Driver;  from .Classes.GnuCash import GnuCash
    from .Eternl import runEternl
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPricesAndShares
    from .HealthEquity import runHealthEquity
    from .IoPay import runIoPay
    from .Worthy import getWorthyBalance
    from .Vanguard import runVanguard401k
    from .Fidelity import runFidelity

def getMonthlyAccounts(type, personalBook, jointBook):
    if type == 'USD':
        IRA, iraSPAXX = USD("IRA", personalBook), Security('IRA SPAXX', personalBook)
        rIRA, riraVXUS, riraVTI, riraSPAXX = USD("Roth IRA", personalBook), Security('Roth IRA VXUS', personalBook), Security('Roth IRA VTI', personalBook), Security('Roth IRA SPAXX', personalBook)
        Brokerage, brSPAXX = USD("Brokerage", personalBook), Security('Brokerage SPAXX', personalBook)
        VIIIX, HECash = Security("HE Investment", personalBook), USD("HE Cash", personalBook)
        VFIAX, OptumCash = Security("Optum Investment", personalBook), USD("Optum Cash", personalBook)
        Pension, V401k, TSM401k, EBI = USD("VanguardPension", personalBook), USD("Vanguard401k", personalBook), Security("Total Stock Market(401k)", personalBook), Security("Employee Benefit Index", personalBook)
        Home, LiquidAssets = USD('Home', jointBook), USD("Liquid Assets", personalBook)
        Bonds, Worthy = USD("Bonds", personalBook), USD("Worthy", personalBook)        
        accounts = {'IRA':IRA,'iraSPAXX':iraSPAXX,'rIRA':rIRA,'riraVXUS':riraVXUS,'riraVTI':riraVTI,'riraSPAXX':riraSPAXX,'Brokerage':Brokerage,'brSPAXX':brSPAXX,
                    'VIIIX':VIIIX,'HECash':HECash,'VFIAX':VFIAX,'OptumCash':OptumCash,'V401k':V401k,'EBI':EBI,'TSM401k':TSM401k,'Worthy': Worthy,'Pension':Pension,
                    'Home':Home,'LiquidAssets':LiquidAssets,'Bonds':Bonds}
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
    account.updateGnuBalance(myBook.getBalance(account.gnuAccount))
    

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
    driver.findWindowByUrl("/scripts/monthly")
    
def runUSD(driver, today, accounts, personalBook):
    lastMonth = getStartAndEndOfDateRange(today, "month")
    getWorthyBalance(driver, accounts['Worthy'])
    monthlyRoundUp(accounts['Worthy'], personalBook, lastMonth['endDate'])
    runHealthEquity(driver, {'VIIIX': accounts['VIIIX'], 'HECash': accounts['HECash'],'V401k': accounts['V401k']}, personalBook)
    accounts['LiquidAssets'].updateGnuBalance(personalBook.getBalance(accounts['LiquidAssets'].gnuAccount))
    accounts['Bonds'].updateGnuBalance(personalBook.getBalance(accounts['Bonds'].gnuAccount))
    runVanguard401k(driver, accounts, personalBook)
    runFidelity(driver, accounts, personalBook)
    updateInvestmentPricesAndShares(driver,personalBook,accounts)
    driver.findWindowByUrl("/scripts/monthly")

def runCrypto(driver, today, accounts, personalBook):
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    runEternl(driver, accounts['Cardano'], personalBook)
    runIoPay(driver, accounts['IoTex'], personalBook)
    # runLedger(accounts['ledgerAccounts'], personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getBalance(accounts['CryptoPortfolio'].gnuAccount))
    driver.findWindowByUrl("/scripts/monthly")

def runMonthlyBank(personalBook, jointBook):
    today = datetime.today().date()
    driver = Driver("Chrome")
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)
    runUSD(driver, today, usdAccounts, personalBook)
    runCrypto(driver, today, cryptoAccounts, personalBook)

if __name__ == '__main__': # USD
    driver = Driver("Chrome")
    today = datetime.today().date()
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    runUSD(driver, today, usdAccounts, personalBook)
    personalBook.closeBook()
    jointBook.closeBook()
    
# if __name__ == '__main__': # Crypto
#     driver = Driver("Chrome")
#     today = datetime.today().date()
#     personalBook = GnuCash('Finance')
#     jointBook = GnuCash('Home')
#     cryptoAccounts = getMonthlyAccounts('Crypto', personalBook, jointBook)    
#     runCrypto(driver, today, cryptoAccounts, personalBook)
#     personalBook.closeBook()
#     jointBook.closeBook()

    # # myBook = openGnuCashBook('Finance', True, True)
    # # getTotalOfAutomatedMRAccounts(myBook)
    
    # driver = Driver("Chrome")
    # vprices = getVanguardPrices(driver)
    # updateInvestmentPrices(driver, jointBook, vprices)
    
    # driver = Driver("Chrome")
    # personalBook = GnuCash('Finance')
    # HealthEquity = USD("HSA", personalBook)
    # healthEquity = getHealthEquityDividendsAndShares(driver, HealthEquity)
    # vanguardInfo = getVanguardPriceAndShares(driver)
    # updateInvestmentShares(driver, HealthEquity, vanguardInfo, fidelity)
    
# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     getEnergyBillAmounts(driver, 201.32)
    