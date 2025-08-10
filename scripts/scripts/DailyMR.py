if __name__ == '__main__' or __name__ == "DailyMR":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from AmazonGC import confirmAmazonGCBalance
    from Paidviewpoint import updatePaidViewPointBalance
    from Pinecone import runPinecone
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
    from InboxDollars import runInboxDollars
else:
    from .Classes.Asset import USD, Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .AmazonGC import confirmAmazonGCBalance
    from .Paidviewpoint import updatePaidViewPointBalance    
    from .Pinecone import runPinecone
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut
    from .InboxDollars import runInboxDollars


def getDailyMRAccounts(personalReadBook):
    AmazonGC = USD("Amazon GC", personalReadBook)
    Pinecone = Security("Pinecone", personalReadBook)
    Swagbucks = Security("Swagbucks", personalReadBook)
    Tellwut = Security("Tellwut", personalReadBook)
    Paidviewpoint = USD("Paidviewpoint", personalReadBook)
    Presearch = Security("Presearch", personalReadBook)
    InboxDollars = USD("InboxDollars", personalReadBook)
    return {'AmazonGC': AmazonGC, 'Pinecone': Pinecone, 'Swagbucks': Swagbucks, 'Tellwut': Tellwut, 'Paidviewpoint': Paidviewpoint, 'Presearch': Presearch, 'InboxDollars': InboxDollars}

def runDailyMR(accounts, book, runAlu=True):
    driver = Driver("Chrome")
    runTellwut(driver, accounts['Tellwut'], book)
    confirmAmazonGCBalance(driver, accounts['AmazonGC'])
    updatePaidViewPointBalance(driver, accounts['Paidviewpoint'], book)
    runPinecone(driver, accounts['Pinecone'], book)
    runSwagbucks(driver, runAlu, accounts['Swagbucks'], book)
    runInboxDollars(driver, accounts['InboxDollars'], book)
    driver.findWindowByUrl("/scripts/daily")
    return True
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    personalBook = GnuCash('Finance')
    accounts = getDailyMRAccounts(personalBook)
    runDailyMR(accounts, personalBook, False)
    personalBook.closeBook()

    