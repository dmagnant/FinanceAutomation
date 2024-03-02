if __name__ == '__main__' or __name__ == "Daily":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getStockPrice 
    from Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet, updateInvestmentPricesAndShares
    from Paypal import runPaypal
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getStockPrice
    from .Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet, updateInvestmentPricesAndShares
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout

def getDailyBankAccounts(personalReadBook, jointReadBook=''):
    CryptoPortfolio = USD("Crypto", personalReadBook)
    Checking = USD("Sofi Checking", personalReadBook)
    Savings = USD("Sofi Savings", personalReadBook)
    Ally = USD("Ally", jointReadBook)
    Presearch = Security("Presearch", personalReadBook)
    return {'CryptoPortfolio': CryptoPortfolio, 'Checking': Checking, 'Savings': Savings, 'Ally': Ally, 'Presearch': Presearch}

def runDailyBank(accounts, personalBook, jointBook):
    driver = Driver("Chrome")
    runSofi(driver, [accounts['Checking'], accounts['Savings']], personalBook)
    # runAlly(driver, accounts['Ally'], jointBook)
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook)
    openSpreadsheet(driver, 'Checking Balance', '2024')
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    updateCryptoPrices(driver, personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook.getBalance(accounts['CryptoPortfolio'].gnuAccount))
    openSpreadsheet(driver, 'Home', '2024 Balance')
    GMEprice = getStockPrice(driver, 'GME')
    personalBook.updatePriceInGnucash('GME', GMEprice)
    personalBook.purgeOldGnucashFiles()
    jointBook.purgeOldGnucashFiles()
    driver.findWindowByUrl("/scripts/daily")
    return GMEprice

def tearDown(driver):
    sofiLogout(driver)
    allyLogout(driver)        
    driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))

if __name__ == '__main__':
    personalBook = GnuCash('Finance')
    jointBook = GnuCash('Home')
    accounts = getDailyBankAccounts(personalBook, jointBook)
    GME = runDailyBank(accounts, personalBook, jointBook)
    personalBook.closeBook()
    jointBook.closeBook()
