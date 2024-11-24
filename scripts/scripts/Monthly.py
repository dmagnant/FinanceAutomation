from decimal import Decimal

if __name__ == '__main__' or __name__ == "Monthly":
    from Classes.Asset import USD, Security;    from Classes.WebDriver import Driver;   from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getStartAndEndOfDateRange, getUsername, getNotes, setDirectory
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentsMonthly, getSheetAndDetails
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
    from .Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateInvestmentsMonthly, getSheetAndDetails
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

def updatePensionBalanceAndCost(driver, book, newBalance):
    Pension = USD('Pension', book)
    newBalance = round(Decimal(newBalance),2)
    # gather amounts
    monthGain = newBalance - Pension.gnuBalance
    employerContributionPerMonth = round(Decimal(813.40),2)
    # write transaction
    splits = [
        book.createSplit(-(monthGain - employerContributionPerMonth),book.getGnuAccountFullName('Interest')), 
        book.createSplit(-employerContributionPerMonth,book.getGnuAccountFullName('Pension Contributions')),
        book.createSplit(monthGain, Pension.gnuAccount)
        ]
    book.writeTransaction(getStartAndEndOfDateRange(timeSpan='month')['endDate'], 'Contribution + Interest', splits)
    # update spreadsheet
    investmentsSheet = getSheetAndDetails('Finances', 'Investments')
    openSpreadsheet(driver, 'Finances', 'Investments')
    row = investmentsSheet['firstRowAfterCrypto']
    while True:
        if investmentsSheet['worksheet'].acell(investmentsSheet['bankColumn']+str(row)).value == 'Pension':
            investmentsSheet['worksheet'].update_acell(investmentsSheet['sharesColumn'] + str(row), float(newBalance))
            investmentsSheet['worksheet'].update_acell(investmentsSheet['costColumn'] + str(row), float(newBalance - Pension.getInterestTotalForDateRange(book)))
            break
        else:
            row+=1
    
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