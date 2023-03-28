if __name__ == '__main__' or __name__ == "Daily":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD, Crypto
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import getStockPrice 
    from Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook, updatePriceInGnucash
    from Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet
    from Paypal import runPaypal
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates, searchUsingPresearch
    from Sofi import runSofi, sofiLogout
    from AmazonGC import confirmAmazonGCBalance
    from Bing import runBing
    from Pinecone import runPinecone
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD, Crypto
    from .Classes.WebDriver import Driver
    from .Functions.GeneralFunctions import getStockPrice
    from .Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook, updatePriceInGnucash
    from .Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet
    from .Paypal import runPaypal
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates, searchUsingPresearch
    from .Sofi import runSofi, sofiLogout
    from .AmazonGC import confirmAmazonGCBalance
    from .Bing import runBing
    from .Pinecone import runPinecone
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut

def getDailyAccounts(type, personalReadBook, jointReadBook=''):
    if type == 'Bank':
        CryptoPortfolio = USD("Crypto", personalReadBook)
        Checking = USD("Sofi Checking", personalReadBook)
        Savings = USD("Sofi Savings", personalReadBook)
        Ally = USD("Ally", jointReadBook)
        Presearch = Crypto("Presearch", personalReadBook)
        accounts = {'CryptoPortfolio': CryptoPortfolio, 'Checking': Checking, 'Savings': Savings, 'Ally': Ally, 'Presearch': Presearch}
    elif type == 'MR':
        AmazonGC = USD("AmazonGC", personalReadBook)
        Bing = Crypto("Bing", personalReadBook)
        Pinecone = Crypto("Pinecone", personalReadBook)
        Swagbucks = Crypto("Swagbucks", personalReadBook)
        Tellwut = Crypto("Tellwut", personalReadBook)
        Paidviewpoint = USD("Paidviewpoint", personalReadBook)
        accounts = {'AmazonGC': AmazonGC, 'Bing': Bing, 'Pinecone': Pinecone, 'Swagbucks': Swagbucks, 'Tellwut': Tellwut, 'Paidviewpoint': Paidviewpoint}
    return accounts

def runDailyBank(accounts, personalBook, jointBook):
    driver = Driver("Chrome")
    runSofi(driver, [accounts['Checking'], accounts['Savings']], personalBook)
    runAlly(driver, accounts['Ally'], jointBook)
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'], personalBook)
    openSpreadsheet(driver, 'Checking Balance', '2023')
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    updateCryptoPrices(driver, personalBook)
    accounts['CryptoPortfolio'].updateGnuBalance(personalBook)
    openSpreadsheet(driver, 'Home', '2023 Balance')
    if accounts['Checking'].reviewTransactions or accounts['Savings'].reviewTransactions:
        openGnuCashUI('Finances')
    if accounts['Ally'].reviewTransactions:
        openGnuCashUI('Home')
    GMEprice = getStockPrice(driver, 'GME')
    updatePriceInGnucash('GME', GMEprice, personalBook)
    purgeOldGnucashFiles()
    return GMEprice

def tearDown(driver):
    sofiLogout(driver)
    allyLogout(driver)        
    driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))

def runDailyMR(accounts, book):
    driver = Driver("Chrome")
    runBing(driver, accounts['Bing'], book)
    searchUsingPresearch(driver)
    runTellwut(driver, accounts['Tellwut'], book)
    confirmAmazonGCBalance(driver, accounts['AmazonGC'])
    runPinecone(driver, accounts['Pinecone'], book)
    searchUsingPresearch(driver)
    runSwagbucks(driver, True, accounts['Swagbucks'], book)
 
if __name__ == '__main__': # Bank
    personalBook = openGnuCashBook('Finance', False, False)
    jointBook = openGnuCashBook('Home', False, False)
    accounts = getDailyAccounts('Bank', personalBook, jointBook)
    GME = runDailyBank(accounts, personalBook, jointBook)
    if not personalBook.is_saved:
        personalBook.save()
    if not jointBook.is_saved:
        jointBook.save()
    personalBook.close()
    jointBook.close()    
# if __name__ == '__main__': # MR
    personalBook = openGnuCashBook('Finance', False, False)
    # accounts = getDailyAccounts('MR', personalBook)
    # runDailyMR(accounts, personalBook)
    if not personalBook.is_saved:
        personalBook.save()
    personalBook.close()
