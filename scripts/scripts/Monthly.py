from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Crypto
    from Classes.WebDriver import Driver
    from Functions.GnuCashFunctions import getGnuCashBalance, getAccountPath
    from Eternl import runEternl
    from Coinbase import runCoinbase
    from Exodus import runExodus
    from Ledger import runLedger
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook, writeGnuTransaction, getTotalOfAutomatedMRAccounts
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPrices
    from HealthEquity import runHealthEquity
    from IoPay import runIoPay
    from Kraken import runKraken
    from MyConstant import runMyConstant
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Worthy import getWorthyBalance 
else:
    from .Classes.Asset import USD, Crypto
    from .Classes.WebDriver import Driver
    from .Functions.GnuCashFunctions import getGnuCashBalance, getAccountPath    
    from .Coinbase import runCoinbase
    from .Eternl import runEternl
    from .Exodus import runExodus
    from .Ledger import runLedger, getLedgerAccounts
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange, showMessage)
    from .Functions.GnuCashFunctions import openGnuCashBook, writeGnuTransaction, getTotalOfAutomatedMRAccounts
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentPrices
    from .HealthEquity import runHealthEquity
    from .IoPay import runIoPay
    from .Kraken import runKraken
    from .MyConstant import runMyConstant
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Worthy import getWorthyBalance

def getMonthlyAccounts(type):
    if type == 'USD':
        Fidelity = USD("Fidelity")
        HealthEquity = USD("HSA")
        V401k = USD("Vanguard401k")
        Pension = USD("VanguardPension")
        Worthy = USD("Worthy")
        accounts = {
            'Fidelity': Fidelity,
            'HealthEquity': HealthEquity,
            'V401k': V401k,
            'Worthy': Worthy,
            'Pension': Pension
        }
    elif type == 'Crypto':
        CryptoPortfolio = USD("Crypto"),
        Cardano = Crypto("Cardano", 'ADA-Eternl')
        Cosmos = Crypto("Cosmos")
        Loopring = Crypto("Loopring")
        IoTex = Crypto("IoTex")
        Ethereum2 = Crypto("Ethereum2")
        ledgerAccounts = getLedgerAccounts()
        accounts = {
            'CryptoPortfolio': CryptoPortfolio,
            'Cardano': Cardano,
            'Cosmos': Cosmos,
            'Loopring': Loopring,
            'IoTex': IoTex,
            'Ethereum2': Ethereum2,
            'ledgerAccounts': ledgerAccounts
        }
    return accounts

def monthlyRoundUp(account, myBook, date, HSADividends):
    change = Decimal(account.balance - float(account.gnuBalance))
    change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":
        transactionVariables = {
            'postDate': date,
            'description': "Interest",
            'amount': -change,
            'fromAccount': account.gnuAccount,
        }
        # writeGnuTransaction(myBook, "Interest", date, -change, "Income:Investments:Interest", account.gnuAccount)
    elif account.name == "HSA":
        HEHSAMarketChange = round(Decimal(change - HSADividends), 2)
        amount = {
            'change': change,
            'HSADividends': -HSADividends,
            'HEHSAMarketChange': -HEHSAMarketChange
        }
        transactionVariables = {
            'postDate': date,
            'description': "HSA Statement",
            'amount': amount,
            'fromAccount': "Income:Investments:Market Change",
        }
        # writeGnuTransaction(myBook, "HSA Statement", date, [change, -HSADividends, -HEHSAMarketChange], ["Income:Investments:Dividends", "Income:Investments:Market Change"], "Assets:Non-Liquid Assets:HSA:NM HSA")
    writeGnuTransaction(myBook, transactionVariables, "Assets:Non-Liquid Assets:HSA:NM HSA")


def runUSD(driver, today, accounts):
    year = today.year
    month = today.month
    lastMonth = getStartAndEndOfDateRange(today, "month")
    myBook = openGnuCashBook('Finance', False, False)
    # MyConstant = runMyConstant(driver, "USD")
    getWorthyBalance(driver, accounts['Worthy'])
    HSA_dividends = runHealthEquity(driver)
    monthlyRoundUp(accounts['Worthy'], myBook, lastMonth['endDate'], HSA_dividends)
    monthlyRoundUp(accounts['HealthEquity'], myBook, lastMonth['endDate'], HSA_dividends)
    LiquidAssets = USD("Liquid Assets")
    Bonds = USD("Bonds")
    openSpreadsheet(driver, 'Asset Allocation', '2022')
    updateSpreadsheet('Asset Allocation', year, Bonds.name, month, float(Bonds.gnuBalance), 'Liquid Assets')
    updateSpreadsheet('Asset Allocation', year, LiquidAssets.name, month, float(LiquidAssets.gnuBalance), 'Liquid Assets')
    updateSpreadsheet('Asset Allocation', year, accounts['V401k'].name, month, accounts['V401k'].balance, '401k')
    updateInvestmentPrices(driver)

def runCrypto(driver, today, accounts):
    year = today.year
    month = today.month
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    runEternl(driver, accounts['Cardano'])
    runKraken(driver, accounts['Ethereum2'])
    runIoPay(driver, accounts['IoTex'])
    runLedger(accounts['ledgerAccounts'])
    runCoinbase(driver, accounts['Loopring'])
    accounts.CryptoPortfolio.updateGnuBalance(openGnuCashBook('Finance', True, True))
    updateSpreadsheet('Asset Allocation', year, accounts['CryptoPortfolio'].name, month, float(round(accounts['CryptoPortfolio'].gnuBalance, 2)), accounts['CryptoPortfolio'].name)

def runMonthlyBank():
    today = datetime.today().date()
    driver = Driver("Chrome")
    usdAccounts = getMonthlyAccounts('USD')
    cryptoAccounts = getMonthlyAccounts('Crypto')
    runUSD(driver, today, usdAccounts)
    runCrypto(driver, today, cryptoAccounts)

if __name__ == '__main__':
    # runMonthlyBank()
    
    # myBook = openGnuCashBook('Finance', True, True)
    # getTotalOfAutomatedMRAccounts(myBook)
    
    driver = Driver("Chrome")
    # Home = USD("Home")
    # updateInvestmentPrices(driver, Home)
    HealthEquity = USD("HSA")
    Vanguard = USD("Vanguard401k")
    HEaccounts = {
        'HealthEquity': HealthEquity, 
        'Vanguard': Vanguard
    }
    today = datetime.today().date()
    myBook = openGnuCashBook('Finance', False, False)
    lastMonth = getStartAndEndOfDateRange(today, "month")
    HSA_dividends = runHealthEquity(driver, HEaccounts)
    monthlyRoundUp(HealthEquity, myBook, lastMonth['endDate'], HSA_dividends)
