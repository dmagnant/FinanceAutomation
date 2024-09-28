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
    from Sofi import runSofi, sofiLogout
    from Fidelity import runFidelityDaily, getFidelityAccounts
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getStartAndEndOfDateRange
    from .Functions.SpreadsheetFunctions import openSpreadsheet, updateInvestmentsDaily, updateInvestmentsDailyAmended
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout
    from. Paypal import runPaypal, checkUncategorizedPaypalTransactions
    from .Fidelity import runFidelityDaily, getFidelityAccounts

def getDailyBankAccounts(personalReadBook, jointReadBook=''):
    CryptoPortfolio = USD("Crypto", personalReadBook)
    Checking = USD("Sofi Checking", personalReadBook)
    Savings = USD("Sofi Savings", personalReadBook)
    Ally = USD("Ally", jointReadBook)
    Presearch = Security("Presearch", personalReadBook)
    Paypal = USD("Paypal", personalReadBook)
    Fidelity = getFidelityAccounts(personalReadBook)
    return {'CryptoPortfolio': CryptoPortfolio, 'Checking': Checking, 'Savings': Savings, 'Ally': Ally, 'Presearch': Presearch, 'Paypal': Paypal, 'Fidelity': Fidelity}

def runDailyBank(accounts, personalBook, jointBook):
    driver = Driver("Chrome")
    runSofi(driver, [accounts['Checking'], accounts['Savings']], personalBook)
    runFidelityDaily(driver, accounts['Fidelity'], personalBook)
    # runAlly(driver, accounts['Ally'], jointBook)
    # presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook)
    openSpreadsheet(driver, 'Finances', str(datetime.today().date().year))
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
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    book = personalBook.getWriteBook()
    from datetime import datetime
    accounts = getDailyBankAccounts(personalBook, jointBook)

    # print(personalBook.getPriceInGnucash('ATOM', datetime.today().date()))
    # updateCryptoPrices(driver, personalBook)
    # updateInvestmentsDaily(driver, personalBook)
    # personalBook.updatePriceInGnucash('ATOM', str(12.06))

    updateInvestmentsDailyAmended(driver, personalBook, accounts)
    personalBook.closeBook()
