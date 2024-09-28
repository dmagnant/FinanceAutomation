if __name__ == '__main__' or __name__ == "Daily":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from AmazonGC import confirmAmazonGCBalance
    from Paidviewpoint import updatePaidViewPointBalance
    from Pinecone import runPinecone
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
else:
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .AmazonGC import confirmAmazonGCBalance
    from .Paidviewpoint import updatePaidViewPointBalance    
    from .Pinecone import runPinecone
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut

def getDailyMRAccounts(personalReadBook):
    AmazonGC = USD("Amazon GC", personalReadBook)
    Pinecone = Security("Pinecone", personalReadBook)
    Swagbucks = Security("Swagbucks", personalReadBook)
    Tellwut = Security("Tellwut", personalReadBook)
    Paidviewpoint = USD("Paidviewpoint", personalReadBook)
    Presearch = Security("Presearch", personalReadBook)
    return {'AmazonGC': AmazonGC, 'Pinecone': Pinecone, 'Swagbucks': Swagbucks, 'Tellwut': Tellwut, 'Paidviewpoint': Paidviewpoint, 'Presearch': Presearch}

def runDailyMR(accounts, book):
    driver = Driver("Chrome")
    runTellwut(driver, accounts['Tellwut'], book)
    confirmAmazonGCBalance(driver, accounts['AmazonGC'])
    updatePaidViewPointBalance(driver, accounts['Paidviewpoint'], book)
    runPinecone(driver, accounts['Pinecone'], book)
    runSwagbucks(driver, True, accounts['Swagbucks'], book)
    driver.findWindowByUrl("/scripts/daily")
    
if __name__ == '__main__':
    personalBook = GnuCash('Finance')
    accounts = getDailyMRAccounts(personalBook)
    runDailyMR(accounts, personalBook)
    personalBook.closeBook()
