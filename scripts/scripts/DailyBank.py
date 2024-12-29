from datetime import datetime
if __name__ == '__main__' or __name__ == "Daily":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Classes.Spreadsheet import Spreadsheet
    from Functions.GeneralFunctions import getStartAndEndOfDateRange
    from Paypal import checkUncategorizedPaypalTransactions
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout, getSofiAccounts
    from Fidelity import runFidelityDaily, getFidelityAccounts, getFidelityAccounts
    from Webull import getWebullAccounts, runWebullDaily
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Classes.Spreadsheet import Spreadsheet
    from .Functions.GeneralFunctions import getStartAndEndOfDateRange
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout, getSofiAccounts
    from. Paypal import runPaypal, checkUncategorizedPaypalTransactions
    from .Fidelity import runFidelityDaily, getFidelityAccounts, getFidelityAccounts
    from .Webull import getWebullAccounts, runWebullDaily

def getDailyBankAccounts(personalBook, jointBook=''):
    CryptoPortfolio = USD("CryptoCurrency", personalBook)
    Sofi = getSofiAccounts(personalBook)
    Ally = USD("Ally", jointBook)
    Presearch = Security("Presearch", personalBook)
    Paypal = USD("Paypal", personalBook)
    Fidelity = getFidelityAccounts(personalBook)
    Webull = getWebullAccounts(personalBook)
    return {'CryptoPortfolio': CryptoPortfolio, 'Sofi':Sofi, 'Ally': Ally, 'Presearch': Presearch, 'Paypal': Paypal, 'Fidelity': Fidelity, 'Webull': Webull}

def runDailyBank(accounts, personalBook, jointBook, gnuCashTransactions, dateRange):
    driver = Driver("Chrome")
    Finances = Spreadsheet('Finances', 'Investments', driver)
    Home = Spreadsheet('Home', '2024 Balance', driver)
    runSofi(driver, accounts['Sofi'], personalBook, gnuCashTransactions, dateRange)
    runFidelityDaily(driver, accounts['Fidelity'], personalBook, gnuCashTransactions, dateRange)
    runWebullDaily(driver, accounts['Webull'], personalBook, gnuCashTransactions, dateRange)
    # runAlly(driver, accounts['Ally'], jointBook, gnuCashTransactions, dateRange)
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook, Finances)
    driver.findWindowByUrl(Finances.url)
    Finances.updateInvestmentsDaily(personalBook, accounts)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['CryptoPortfolio'].gnuAccount))
    checkUncategorizedPaypalTransactions(driver, personalBook, accounts['Paypal'], getStartAndEndOfDateRange(timeSpan=7))
    personalBook.purgeOldGnucashFiles()
    jointBook.purgeOldGnucashFiles()
    driver.findWindowByUrl("/scripts/daily")
    
def tearDown(driver):
    sofiLogout(driver)
    # allyLogout(driver)        
    driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))

# if __name__ == '__main__':
#     personalBook = GnuCash('Finance')
#     jointBook = GnuCash('Home')
#     accounts = getDailyBankAccounts(personalBook, jointBook)
#     dateRange = getStartAndEndOfDateRange(timeSpan=7)
#     gnuCashTransactions = personalBook.getTransactionsByDateRange(dateRange)
#     GME = runDailyBank(accounts, personalBook, jointBook)
#     personalBook.closeBook()
#     jointBook.closeBook()


if __name__ == '__main__':
    driver = Driver("Chrome")
    # personalBook = GnuCash('Finance')
    # jointBook = GnuCash('Home')
    # book = personalBook.getWriteBook()
    # from datetime import datetime
    # openSpreadsheet(driver, 'Home', '2024 Balance')
    Finances = Spreadsheet('Finances', 'Investments', driver)


    driver.findWindowByUrl(Finances.url)