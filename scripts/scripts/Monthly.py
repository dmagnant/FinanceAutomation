from datetime import datetime
from decimal import Decimal
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Eternl import runEternl
    from Coinbase import runCoinbase
    from Exodus import runExodus
    from Ledger import runLedger, getLedgerAccounts
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange)
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPricesAndShares
    from HealthEquity import runHealthEquity
    from IoPay import runIoPay
    from Kraken import runKraken
    from MyConstant import runMyConstant
    from Worthy import getWorthyBalance 
    from Sofi import setMonthlySpendTarget
    from Vanguard import runVanguard401k
    from Fidelity import runFidelity
else:
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Coinbase import runCoinbase
    from .Eternl import runEternl
    from .Exodus import runExodus
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPricesAndShares
    from .HealthEquity import runHealthEquity
    from .IoPay import runIoPay
    from .Kraken import runKraken
    from .MyConstant import runMyConstant
    from .Worthy import getWorthyBalance
    from .Sofi import setMonthlySpendTarget
    from .Vanguard import runVanguard401k
    from .Fidelity import runFidelity

def getMonthlyAccounts(type, personalBook, jointBook):
    if type == 'USD':
        IRA = USD("IRA", personalBook)
        iraSPAXX = Security('IRA SPAXX', personalBook)
        rIRA = USD("Roth IRA", personalBook)
        riraVXUS = Security('Roth IRA VXUS', personalBook)
        riraVTI = Security('Roth IRA VTI', personalBook)
        riraSPAXX = Security('Roth IRA SPAXX', personalBook)
        Brokerage = USD("Brokerage", personalBook)
        brSPAXX = brSPAXX = Security('Brokerage SPAXX', personalBook)
        VIIIX = Security("HSA Investment", personalBook)
        HECash = USD("HSA Cash", personalBook)
        VFIAX = Security("SF HSA Investment", personalBook)
        OptumCash = USD("Optum Cash", personalBook)
        V401k = USD("Vanguard401k", personalBook)
        Pension = USD("VanguardPension", personalBook)
        TSM401k = Security("Total Stock Market(401k)", personalBook)
        EBI = Security("Employee Benefit Index", personalBook)
        Worthy = USD("Worthy", personalBook)
        Home = USD('Home', jointBook)
        LiquidAssets = USD("Liquid Assets", personalBook)
        Bonds = USD("Bonds", personalBook)
        accounts = {'IRA':IRA,'iraSPAXX':iraSPAXX,'rIRA':rIRA,'riraVXUS':riraVXUS,'riraVTI':riraVTI,'riraSPAXX':riraSPAXX,'Brokerage':Brokerage,'brSPAXX':brSPAXX,
                    'VIIIX':VIIIX,'HECash':HECash,'VFIAX':VFIAX,'OptumCash':OptumCash,'V401k':V401k,'EBI':EBI,'TSM401k':TSM401k,'Worthy': Worthy,'Pension':Pension,
                    'Home':Home,'LiquidAssets':LiquidAssets,'Bonds':Bonds}
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto", personalBook)
        Cardano = Security("Cardano", personalBook, 'ADA-Eternl')
        Cosmos = Security("Cosmos", personalBook)
        IoTex = Security("IoTex", personalBook)
        ledgerAccounts = getLedgerAccounts(personalBook)
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Cardano': Cardano, 'Cosmos': Cosmos, 'IoTex': IoTex, 'ledgerAccounts': ledgerAccounts}
    return accounts

def monthlyRoundUp(account, myBook, date):
    change = Decimal(account.balance - float(account.gnuBalance))
    change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":
        transactionVariables = {'postDate': date, 'description': "Interest", 'amount': -change, 'fromAccount': "Income:Investments:Interest"}
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
    except NoSuchElementException:
        exception = "caught"
    driver.webDriver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click() # view bill history
    time.sleep(4)
    billRow = 2
    billColumn = 7
    billNotFound = True
    while billNotFound:
        weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
        weBillAmount = driver.webDriver.find_element(By.XPATH, weBillPath).text.replace('$', '')
        if amount == weBillAmount:
            billNotFound = False
        else:
            billRow += 1
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
    setMonthlySpendTarget(driver)
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
    