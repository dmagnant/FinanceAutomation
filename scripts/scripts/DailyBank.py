from datetime import datetime
if __name__ == '__main__' or __name__ == "DailyBank":
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
    from Vanguard import vanguardStalePriceCheck
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
    from .Vanguard import vanguardStalePriceCheck


def getDailyBankAccounts(personalBook, jointBook=''):
    CryptoPortfolio = USD("CryptoCurrency", personalBook)
    Sofi = getSofiAccounts(personalBook)
    Ally = USD("Ally", jointBook)
    Presearch = Security("Presearch", personalBook)
    Paypal = USD("Paypal", personalBook)
    Fidelity = getFidelityAccounts(personalBook)
    Webull = getWebullAccounts(personalBook)
    return {'CryptoPortfolio': CryptoPortfolio, 'Sofi':Sofi, 'Ally': Ally, 'Presearch': Presearch, 'Paypal': Paypal, 'Fidelity': Fidelity, 'Webull': Webull}

def runDailyBank(driver, accounts, personalBook, jointBook, gnuCashTransactions, dateRange):
    Finances = Spreadsheet('Finances', 'Investments', driver)
    Home = Spreadsheet('Home', '2026 Balance', driver)
    runSofi(driver, accounts['Sofi'], personalBook, gnuCashTransactions, dateRange)
    runFidelityDaily(driver, accounts['Fidelity'], personalBook, gnuCashTransactions, dateRange)
    runWebullDaily(driver, accounts['Webull'], personalBook, gnuCashTransactions, dateRange)
    # runAlly(driver, accounts['Ally'], jointBook, gnuCashTransactions, dateRange)
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook, Finances)
    driver.findWindowByUrl(Finances.url)
    vanguard = vanguardStalePriceCheck(driver, personalBook)
    Finances.updateInvestmentsDaily(personalBook, accounts, vanguard)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['CryptoPortfolio'].gnuAccount))
    checkUncategorizedPaypalTransactions(driver, personalBook, accounts['Paypal'], getStartAndEndOfDateRange(timeSpan=7))
    personalBook.purgeOldGnucashFiles()
    jointBook.purgeOldGnucashFiles()
    driver.findWindowByUrl("/scripts/daily")
    return True
    
def tearDown(driver):
    sofiLogout(driver)
    # allyLogout(driver)        
    driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))

# if __name__ == '__main__':
    # driver = Driver("Chrome")
#     personalBook = GnuCash('Finance')
#     jointBook = GnuCash('Home')
#     accounts = getDailyBankAccounts(personalBook, jointBook)
#     dateRange = getStartAndEndOfDateRange(timeSpan=7)
#     gnuCashTransactions = personalBook.getTransactionsByDateRange(dateRange)
#     GME = runDailyBank(driver, accounts, personalBook, jointBook)
#     personalBook.closeBook()
#     jointBook.closeBook()


if __name__ == '__main__':
    driver = Driver("Chrome")
    personalBook = GnuCash('Finance')
    # jointBook = GnuCash('Home')
    book = personalBook.getWriteBook()
    # from datetime import datetime
    # openSpreadsheet(driver, 'Home', '2024 Balance')
    # accounts = getDailyBankAccounts(personalBook, jointBook)
    Finances = Spreadsheet('Finances', 'Investments', driver)
    book.closeBook()