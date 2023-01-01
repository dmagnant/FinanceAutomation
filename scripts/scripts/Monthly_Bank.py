from datetime import datetime
from decimal import Decimal
import pygetwindow

if __name__ == '__main__' or __name__ == "Monthly_Bank":
    from Classes.Asset import USD, Crypto
    from Classes.WebDriver import Driver
    from Eternl import runEternl
    from Exodus import runExodus
    from Ledger import runLedger
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook, writeGnuTransaction, getTotalOfAutomatedMRAccounts
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
    from HealthEquity import getHealthEquityBalances
    from IoPay import runIoPay
    from Kraken import runKraken
    from MyConstant import runMyConstant
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Worthy import getWorthyBalance 
else:
    from .Classes.Asset import USD, Crypto
    from .Classes.WebDriver import Driver
    from .Eternl import runEternl
    from .Exodus import runExodus
    from .Ledger import runLedger
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import openGnuCashBook, writeGnuTransaction, getTotalOfAutomatedMRAccounts
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
    from .HealthEquity import getHealthEquityBalances
    from .IoPay import runIoPay
    from .Kraken import runKraken
    from .MyConstant import runMyConstant
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Worthy import getWorthyBalance

def monthlyRoundUp(account, myBook, date, HSADividends):
    change = Decimal(account.balance - float(account.gnuBalance))
    change = round(change, 2)
    if account.name == "MyConstant" or account.name == "Worthy":
        writeGnuTransaction(myBook, "Interest", date, -change, "Income:Investments:Interest", account.gnuAccount)
    elif account.name == "HSA":
        HEHSAMarketChange = round(Decimal(change - HSADividends), 2)
        writeGnuTransaction(myBook, "HSA Statement", date, [change, -HSADividends, -HEHSAMarketChange], ["Income:Investments:Dividends", "Income:Investments:Market Change"], "Assets:Non-Liquid Assets:HSA:NM HSA")

def runUSD(driver, today):
    directory = setDirectory()
    year = today.year
    month = today.month
    lastMonth = getStartAndEndOfDateRange(today, today.month, today.year, "month")
    myBook = openGnuCashBook('Finance', False, False)
    MyConstant = runMyConstant(driver, "USD")
    Worthy = getWorthyBalance(driver)
    healthEquityHSADividendsAndVanguard = getHealthEquityBalances(driver, lastMonth)
    for account in [MyConstant, Worthy, healthEquityHSADividendsAndVanguard[0]]:
        monthlyRoundUp(account, myBook, lastMonth[1], healthEquityHSADividendsAndVanguard[1])
    LiquidAssets = USD("Liquid Assets")
    Bonds = USD("Bonds")
    openSpreadsheet(driver.webDriver, 'Asset Allocation', '2022')
    updateSpreadsheet(directory, 'Asset Allocation', year, Bonds.name, month, float(Bonds.gnuBalance), 'Liquid Assets')
    updateSpreadsheet(directory, 'Asset Allocation', year, LiquidAssets.name, month, float(LiquidAssets.gnuBalance), 'Liquid Assets')
    updateSpreadsheet(directory, 'Asset Allocation', year, healthEquityHSADividendsAndVanguard[2].name, month, healthEquityHSADividendsAndVanguard[2].balance, '401k')
    return [MyConstant, Worthy, LiquidAssets, healthEquityHSADividendsAndVanguard[2], healthEquityHSADividendsAndVanguard[0]]

def runCrypto(driver, today):
    directory = setDirectory()
    year = today.year
    month = today.month
    Crypto = USD("Crypto")
    openSpreadsheet(driver.webDriver, 'Asset Allocation', 'Cryptocurrency')
    runEternl(driver)
    runKraken(driver)
    presearchRewardsRedemptionAndBalanceUpdates(driver)
    runIoPay(driver)
    runLedger()
    Crypto.updateGnuBalance(openGnuCashBook('Finance', True, True))
    updateSpreadsheet(directory, 'Asset Allocation', year, Crypto.name, month, float(round(Crypto.gnuBalance, 2)), Crypto.name)
    return Crypto

def runMonthlyBank():
    today = datetime.today()
    driver = Driver("Chrome")
    usdbalances = runUSD(driver, today)
    cryptoPortfolio = runCrypto(driver, today)
    showMessage("Balances", 
                f'MyConstant: {usdbalances[0].balance} \n' 
                f'Worthy: {usdbalances[1].balance} \n' 
                f'Liquid Assets: {usdbalances[2].balance} \n' 
                f'401k: {usdbalances[3].balance} \n'
                f'NM HSA: {usdbalances[4].balance} \n'
                f'Crypto Portfolio worth: {cryptoPortfolio.gnuBalance}')

    while len(driver.webDriver.window_handles) > 1:
        driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
        driver.webDriver.close()

if __name__ == '__main__':
    # runMonthlyBank()
    
    myBook = openGnuCashBook('Finance', True, True)
    getTotalOfAutomatedMRAccounts(myBook)