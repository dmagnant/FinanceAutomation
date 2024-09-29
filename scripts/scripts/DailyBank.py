from datetime import datetime
if __name__ == '__main__' or __name__ == "Daily":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getStartAndEndOfDateRange
    from Functions.SpreadsheetFunctions import openSpreadsheet, updateInvestmentsDaily, updateInvestmentsDailyAmended
    from Paypal import runPaypal, checkUncategorizedPaypalTransactions
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout, getSofiAccounts
    from Fidelity import runFidelityDaily, getFidelityAccounts
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getStartAndEndOfDateRange
    from .Functions.SpreadsheetFunctions import openSpreadsheet, updateInvestmentsDaily, updateInvestmentsDailyAmended
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout, getSofiAccounts
    from. Paypal import runPaypal, checkUncategorizedPaypalTransactions
    from .Fidelity import runFidelityDaily, getFidelityAccounts

def getDailyBankAccounts(personalBook, jointBook=''):
    CryptoPortfolio = USD("Crypto", personalBook)
    Sofi = getSofiAccounts(personalBook)
    Ally = USD("Ally", jointBook)
    Presearch = Security("Presearch", personalBook)
    Paypal = USD("Paypal", personalBook)
    Fidelity = getFidelityAccounts(personalBook)
    return {'CryptoPortfolio': CryptoPortfolio, 'Sofi':Sofi, 'Ally': Ally, 'Presearch': Presearch, 'Paypal': Paypal, 'Fidelity': Fidelity}

def runDailyBank(accounts, personalBook, jointBook):
    driver = Driver("Chrome")
    today = datetime.today().date()
    runSofi(driver, accounts['Sofi'], personalBook)
    runFidelityDaily(driver, accounts['Fidelity'], personalBook)
    # runAlly(driver, accounts['Ally'], jointBook)
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook)
    openSpreadsheet(driver, 'Finances', str(today.year))
    # updateInvestmentsDaily(driver, personalBook)
    updateInvestmentsDailyAmended(driver, personalBook, accounts)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getGnuAccountBalance(accounts['CryptoPortfolio'].gnuAccount))
    checkUncategorizedPaypalTransactions(driver, personalBook, accounts['Paypal'], getStartAndEndOfDateRange(timeSpan=7))
    openSpreadsheet(driver, 'Home', '2024 Balance')
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
#     GME = runDailyBank(accounts, personalBook, jointBook)
#     personalBook.closeBook()
#     jointBook.closeBook()


if __name__ == '__main__':
    driver = Driver("Chrome")
    # personalBook = GnuCash('Finance')
    # jointBook = GnuCash('Home')
    # book = personalBook.getWriteBook()
    # from datetime import datetime
    openSpreadsheet(driver, 'Finances', str(datetime.today().date().year))