from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Eternl import runEternl
    from Coinbase import runCoinbase
    from Exodus import runExodus
    from Ledger import runLedger
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
        Fidelity = USD("Fidelity", personalBook)
        VIIIX = Security("HSA Investment", personalBook)
        HECash = USD("HSA Cash", personalBook)
        V401k = USD("Vanguard401k", personalBook)
        Pension = USD("VanguardPension", personalBook)
        REIF401k = Security("Real Estate Index Fund", personalBook)
        TSM401k = Security("Total Stock Market(401k)", personalBook)
        VXUS = Security('Total Intl Stock Market', personalBook)
        VTI = Security('Total Stock Market(IRA)', personalBook)
        SPAXX = Security('Govt Money Market', personalBook)
        Worthy = USD("Worthy", personalBook)
        Home = USD('Home', jointBook)
        LiquidAssets = USD("Liquid Assets", personalBook)
        Bonds = USD("Bonds", personalBook)
        accounts = {'Fidelity':Fidelity,'VXUS':VXUS,'VTI':VTI,'SPAXX':SPAXX,'VIIIX':VIIIX,'HECash':HECash,'V401k':V401k,'REIF401k':REIF401k,'TSM401k':TSM401k,'Worthy': Worthy,'Pension':Pension,'Home':Home,'LiquidAssets':LiquidAssets,'Bonds':Bonds}
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto", personalBook)
        Cardano = Security("Cardano", personalBook, 'ADA-Eternl')
        Cosmos = Security("Cosmos", personalBook)
        Loopring = Security("Loopring", personalBook)
        IoTex = Security("IoTex", personalBook)
        ledgerAccounts = getLedgerAccounts(personalBook)
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Cardano': Cardano, 'Cosmos': Cosmos, 'Loopring': Loopring, 'IoTex': IoTex, 'ledgerAccounts': ledgerAccounts}
    return accounts

def monthlyRoundUp(account, myBook, date):
    change = Decimal(account.balance - float(account.gnuBalance))
    change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":
        transactionVariables = {'postDate': date, 'description': "Interest", 'amount': -change, 'fromAccount': "Income:Investments:Interest"}
    myBook.writeGnuTransaction(transactionVariables, account.gnuAccount)
    account.updateGnuBalance(myBook.getBalance(account.gnuAccount))
    
def runUSD(driver, today, accounts, personalBook):
    lastMonth = getStartAndEndOfDateRange(today, "month")
    setMonthlySpendTarget(driver)
    getWorthyBalance(driver, accounts['Worthy'])
    runHealthEquity(driver, {'VIIIX': accounts['VIIIX'], 'HECash': accounts['HECash'],'V401k': accounts['V401k']}, personalBook)
    monthlyRoundUp(accounts['Worthy'], personalBook, lastMonth['endDate'])
    accounts['LiquidAssets'].updateGnuBalance(personalBook.getBalance(accounts['LiquidAssets'].gnuAccount))
    accounts['Bonds'].updateGnuBalance(personalBook.getBalance(accounts['Bonds'].gnuAccount))
    runVanguard401k(driver, accounts, personalBook)
    runFidelity(driver, accounts, personalBook)
    updateInvestmentPricesAndShares(driver, accounts, personalBook)
    driver.findWindowByUrl("/scripts/monthly")

def runCrypto(driver, today, accounts, personalBook):
    year = today.year
    month = today.month
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

if __name__ == '__main__':
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    runMonthlyBank(personalBook, jointBook)
    personalBook.closeBook()
    jointBook.closeBook()


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
