from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Crypto
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Eternl import runEternl
    from Coinbase import runCoinbase
    from Exodus import runExodus
    from Ledger import runLedger
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange)
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPrices, updateInvestmentShares
    from HealthEquity import runHealthEquity, getHealthEquityDividendsAndShares
    from IoPay import runIoPay
    from Kraken import runKraken
    from MyConstant import runMyConstant
    from Worthy import getWorthyBalance 
    from Sofi import setMonthlySpendTarget
    from Vanguard import getVanguardPriceAndShares
    from Fidelity import getFidelityShares
else:
    from .Classes.Asset import USD, Crypto
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Coinbase import runCoinbase
    from .Eternl import runEternl
    from .Exodus import runExodus
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPrices, updateInvestmentShares
    from .HealthEquity import runHealthEquity, getHealthEquityDividendsAndShares
    from .IoPay import runIoPay
    from .Kraken import runKraken
    from .MyConstant import runMyConstant
    from .Worthy import getWorthyBalance
    from .Sofi import setMonthlySpendTarget
    from .Vanguard import getVanguardPriceAndShares
    from .Fidelity import getFidelityShares

def getMonthlyAccounts(type, personalBook, jointBook):
    if type == 'USD':
        Fidelity = USD("Fidelity", personalBook)
        HealthEquity = USD("HSA", personalBook)
        V401k = USD("Vanguard401k", personalBook)
        Pension = USD("VanguardPension", personalBook)
        Worthy = USD("Worthy", personalBook)
        Home = USD('Home', jointBook)
        LiquidAssets = USD("Liquid Assets", personalBook)
        Bonds = USD("Bonds", personalBook)
        accounts = {'Fidelity': Fidelity, 'HealthEquity': HealthEquity, 'V401k': V401k, 'Worthy': Worthy, 'Pension': Pension, 'Home': Home, 'LiquidAssets': LiquidAssets, 'Bonds': Bonds}
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto", personalBook)
        Cardano = Crypto("Cardano", personalBook, 'ADA-Eternl')
        Cosmos = Crypto("Cosmos", personalBook)
        Loopring = Crypto("Loopring", personalBook)
        IoTex = Crypto("IoTex", personalBook)
        ledgerAccounts = getLedgerAccounts(personalBook)
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Cardano': Cardano, 'Cosmos': Cosmos, 'Loopring': Loopring, 'IoTex': IoTex, 'ledgerAccounts': ledgerAccounts}
    return accounts

def monthlyRoundUp(account, myBook, date, HSADividends):
    change = Decimal(account.balance - float(account.gnuBalance))
    change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":
        transactionVariables = {'postDate': date, 'description': "Interest", 'amount': -change, 'fromAccount': "Income:Investments:Interest"}
    elif account.name == "HSA":
        HEHSAMarketChange = round(Decimal(change - HSADividends), 2)
        amount = {'change': change, 'HSADividends': -HSADividends, 'HEHSAMarketChange': -HEHSAMarketChange}
        transactionVariables = {'postDate': date, 'description': "HSA Statement", 'amount': amount, 'fromAccount': "Income:Investments:Market Change"}
    myBook.writeGnuTransaction(transactionVariables, account.gnuAccount)
    account.updateGnuBalance(myBook.getBalance(account.gnuAccount))
    
def runUSD(driver, today, accounts, personalBook):
    year = today.year
    month = today.month
    lastMonth = getStartAndEndOfDateRange(today, "month")
    setMonthlySpendTarget(driver)
    getWorthyBalance(driver, accounts['Worthy'])
    HEaccounts = {'HealthEquity': accounts['HealthEquity'], 'V401k': accounts['V401k']}
    HSA_dividends = runHealthEquity(driver, HEaccounts)
    monthlyRoundUp(accounts['Worthy'], personalBook, lastMonth['endDate'], HSA_dividends)
    monthlyRoundUp(accounts['HealthEquity'], personalBook, lastMonth['endDate'], HSA_dividends)
    accounts['LiquidAssets'].updateGnuBalance(personalBook.getBalance(accounts['LiquidAssets'].gnuAccount))
    accounts['Bonds'].updateGnuBalance(personalBook.getBalance(accounts['Bonds'].gnuAccount))
    openSpreadsheet(driver, 'Asset Allocation', str(year))
    updateSpreadsheet('Asset Allocation', year, accounts['Bonds'].name, month, float(accounts['Bonds'].gnuBalance), 'Liquid Assets')
    updateSpreadsheet('Asset Allocation', year, accounts['LiquidAssets'].name, month, float(accounts['LiquidAssets'].gnuBalance), 'Liquid Assets')
    updateSpreadsheet('Asset Allocation', year, accounts['V401k'].name, month, accounts['V401k'].balance, '401k')
    vanguardInfo = getVanguardPriceAndShares(driver)
    updateInvestmentPrices(driver, accounts['Home'], vanguardInfo['price8585'])
    fidelity = getFidelityShares(driver)
    updateInvestmentShares(driver, accounts['HealthEquity'], vanguardInfo, fidelity)
    driver.findWindowByUrl("/scripts/monthly")

def runCrypto(driver, today, accounts, personalBook):
    year = today.year
    month = today.month
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    runEternl(driver, accounts['Cardano'], personalBook)
    runIoPay(driver, accounts['IoTex'], personalBook)
    # runLedger(accounts['ledgerAccounts'], personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getBalance(accounts['CryptoPortfolio'].gnuAccount))
    updateSpreadsheet('Asset Allocation', year, accounts['CryptoPortfolio'].name, month, float(round(accounts['CryptoPortfolio'].gnuBalance, 2)), accounts['CryptoPortfolio'].name)
    driver.findWindowByUrl("/scripts/monthly")

def runMonthlyBank(personalBook, jointBook):
    today = datetime.today().date()
    driver = Driver("Chrome")
    usdAccounts = getMonthlyAccounts('USD', personalBook, jointBook)
    cryptoAccounts = getMonthlyAccounts('Crypto', personalBook)
    runUSD(driver, today, usdAccounts, personalBook, jointBook)
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
    # fidelity = getFidelityShares(driver)
    # updateInvestmentShares(driver, HealthEquity, vanguardInfo, fidelity)
    