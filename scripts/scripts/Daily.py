if __name__ == '__main__' or __name__ == "Daily":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD, Crypto
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import showMessage, getStockPrice
    from Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook, getPriceInGnucash, updatePriceInGnucash
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
    from .Functions.GeneralFunctions import showMessage, getStockPrice
    from .Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook, getPriceInGnucash, updatePriceInGnucash
    from .Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet
    from .Paypal import runPaypal
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates, searchUsingPresearch
    from .Sofi import runSofi, sofiLogout
    from .AmazonGC import confirmAmazonGCBalance
    from .Bing import runBing
    from .Pinecone import runPinecone
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut

def getDailyAccounts(type):
    accounts = dict()
    if type == 'Bank':
        CryptoPortfolio = USD("Crypto")
        Checking = USD("Sofi Checking")
        Savings = USD("Sofi Savings")
        Ally = USD("Ally")
        Presearch = Crypto("Presearch")
        accounts = {
            'CryptoPortfolio': CryptoPortfolio,
            'Checking': Checking,
            'Savings': Savings,
            'Ally': Ally,
            'Presearch': Presearch
        }
    elif type == 'MR':
        AmazonGC = USD("AmazonGC")
        Bing = Crypto("Bing")
        Pinecone = Crypto("Pinecone")
        Swagbucks = Crypto("Swagbucks")
        Tellwut = Crypto("Tellwut")
        Paidviewpoint = USD("Paidviewpoint")
        accounts = {
            'AmazonGC': AmazonGC,
            'Bing': Bing,
            'Pinecone': Pinecone,
            'Swagbucks': Swagbucks,
            'Tellwut': Tellwut,
            'Paidviewpoint': Paidviewpoint
        }
    return accounts

def runDailyBank(accounts):
    driver = Driver("Chrome")
    runSofi(driver, [accounts['Checking'], accounts['Savings']])
    runAlly(driver, accounts['Ally'])
    presearchRewardsRedemptionAndBalanceUpdates(driver, accounts['Presearch'])
    runPaypal(driver)
    openSpreadsheet(driver, 'Checking Balance', '2023')
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    updateCryptoPrices(driver)
    accounts['CryptoPortfolio'].updateGnuBalance(openGnuCashBook('Finance', True, True))
    openSpreadsheet(driver, 'Home', '2023 Balance')
    if accounts['Checking'].reviewTransactions or accounts['Savings'].reviewTransactions:
        openGnuCashUI('Finances')
    if accounts['Ally'].reviewTransactions:
        openGnuCashUI('Home')
    GMEprice = getStockPrice(driver, 'GME')
    updatePriceInGnucash('GME', GMEprice)
    purgeOldGnucashFiles()
    return GMEprice

def tearDown(driver):
    sofiLogout(driver)
    allyLogout(driver)        
    driver.closeWindowsExcept([':8000/'], driver.findWindowByUrl("scripts/daily"))

def runDailyMR(accounts):
    driver = Driver("Chrome")
    runBing(driver, accounts['Bing'])
    searchUsingPresearch(driver)
    runTellwut(driver, accounts['Tellwut'])
    confirmAmazonGCBalance(driver, accounts['AmazonGC'])
    runPinecone(driver, accounts['Pinecone'])
    searchUsingPresearch(driver)
    runSwagbucks(driver, True, accounts['Swagbucks'])
 
# if __name__ == '__main__': # Bank
    # accounts = getDailyAccounts('Bank')
    # GME = runDailyBank(accounts)
    
# if __name__ == '__main__': # MR
    # accounts = getDailyAccounts('MR')
    # runDailyMR(accounts)