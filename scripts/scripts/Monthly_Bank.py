from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Monthly_Bank":
    from Functions.GeneralFunctions import showMessage, setDirectory, getStartAndEndOfDateRange
    from Functions.WebDriverFunctions import openWebDriver
    from Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance, writeGnuTransaction
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Eternl import runEternl
    from Exodus import runExodus
    from HealthEquity import runHealthEquity
    from IoPay import runIoPay
    from Kraken import runKraken
    from Midas import runMidas
    from MyConstant import runMyConstant
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Worthy import runWorthy
else:
    from .Functions.GeneralFunctions import showMessage, setDirectory, getStartAndEndOfDateRange
    from .Functions.WebDriverFunctions import openWebDriver
    from .Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance, writeGnuTransaction
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Eternl import runEternl
    from .Exodus import runExodus
    from .HealthEquity import runHealthEquity
    from .IoPay import runIoPay
    from .Kraken import runKraken
    from .Midas import runMidas
    from .MyConstant import runMyConstant
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Worthy import runWorthy    

def runUSD(driver, today):
    directory = setDirectory()
    year = today.year
    month = today.month
    lastMonth = getStartAndEndOfDateRange(today, today.month, today.year, "month")
    myConstantBalance = runMyConstant(driver, "USD")
    worthyBalance = runWorthy(driver)
    HEBalances = runHealthEquity(driver, lastMonth)

    mybook = openGnuCashBook('Finance', False, False)
    constantInterest = Decimal(myConstantBalance - float(getGnuCashBalance(mybook, 'MyConstant')))
    worthyInterest = Decimal(worthyBalance - float(getGnuCashBalance(mybook, 'Worthy')))
    HEHSAChange = round(Decimal(HEBalances[0] - float(getGnuCashBalance(mybook, 'HSA'))), 2)
    HEHSAMarketChange = round(Decimal(HEHSAChange - HEBalances[1]), 2)

    writeGnuTransaction(mybook, "Interest", lastMonth[1], -round(constantInterest, 2), "Income:Investments:Interest", "Assets:Liquid Assets:Bonds:My Constant")
    writeGnuTransaction(mybook, "Interest", lastMonth[1], -round(worthyInterest, 2), "Income:Investments:Interest", "Assets:Liquid Assets:Bonds:Worthy Bonds")
    writeGnuTransaction(mybook, "HSA Statement", lastMonth[1], [HEHSAChange, -HEBalances[1], -HEHSAMarketChange], ["Income:Investments:Dividends", "Income:Investments:Market Change"], "Assets:Non-Liquid Assets:HSA:NM HSA")

    liquidAssets = getGnuCashBalance(mybook, 'Liquid Assets')
    bonds = getGnuCashBalance(mybook, 'Bonds')

    updateSpreadsheet(directory, 'Asset Allocation', year, 'Bonds', month, float(bonds), 'Liquid Assets')
    updateSpreadsheet(directory, 'Asset Allocation', year, 'Liquid Assets', month, float(liquidAssets), 'Liquid Assets')
    updateSpreadsheet(directory, 'Asset Allocation', year, 'Vanguard401k', month, HEBalances[2], '401k')
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=2058576150');")

    return [myConstantBalance, worthyBalance, liquidAssets, HEBalances[2], HEBalances[0]]

def runCrypto(driver, today):
    directory = setDirectory()
    year = today.year
    month = today.month
    driver.implicitly_wait(5)
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=623829469');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    # runMyConstant(driver, "Crypto")
    runEternl(driver)
    runKraken(driver)
    presearchRewardsRedemptionAndBalanceUpdates(driver)
    # runMidas(driver)
    runExodus()
    runIoPay()
    Finance = openGnuCashBook('Finance', True, True)
    cryptoBalance = round(getGnuCashBalance(Finance, 'Crypto'), 2)
    updateSpreadsheet(directory, 'Asset Allocation', year, 'Cryptocurrency', month, float(cryptoBalance), 'Cryptocurrency')
    return cryptoBalance

def runMonthlyBank():
    today = datetime.today()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(6)
    usdbalances = runUSD(driver, today)
    cryptoBalance = runCrypto(driver, today)
    showMessage("Balances", 
                f'MyConstant: {usdbalances[0]} \n' 
                f'Worthy: {usdbalances[1]} \n' 
                f'Liquid Assets: {usdbalances[2]} \n' 
                f'401k: {usdbalances[3]} \n'
                f'NM HSA: {usdbalances[4]} \n'
                f'Crypto Portfolio worth: {cryptoBalance}')

    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.close()

if __name__ == '__main__':
    runMonthlyBank()
