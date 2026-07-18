if __name__ == '__main__' or __name__ == "DailyMR":
    from Classes.Asset import USD, Security
    from Classes.Selenium import WebDriver
    from Classes.GnuCash import GnuCash
    from AmazonGC import confirmAmazonGCBalance
    from Paidviewpoint import updatePaidViewPointBalance
    from Pinecone import runPinecone
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
    from InboxDollars import runInboxDollars
    from MyPoints import runMyPoints
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .AmazonGC import confirmAmazonGCBalance
    from .Paidviewpoint import updatePaidViewPointBalance    
    from .Pinecone import runPinecone
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut
    from .InboxDollars import runInboxDollars
    from .MyPoints import runMyPoints



def getDailyMRAccounts(personalReadBook):
    AmazonGC = USD("Amazon GC", personalReadBook)
    Pinecone = Security("Pinecone", personalReadBook)
    Swagbucks = Security("Swagbucks", personalReadBook)
    Tellwut = Security("Tellwut", personalReadBook)
    Paidviewpoint = USD("Paidviewpoint", personalReadBook)
    # Presearch = Security("Presearch", personalReadBook)
    InboxDollars = USD("InboxDollars", personalReadBook)
    MyPoints = Security("MyPoints", personalReadBook)
    return {'AmazonGC': AmazonGC, 'Pinecone': Pinecone, 'Swagbucks': Swagbucks, 'Tellwut': Tellwut, 'Paidviewpoint': Paidviewpoint, 'InboxDollars': InboxDollars, 'MyPoints': MyPoints}

def runDailyMR(driver, accounts, book, dailyGame=True):
    runTellwut(driver, accounts['Tellwut'], book)
    confirmAmazonGCBalance(driver, accounts['AmazonGC'])
    updatePaidViewPointBalance(driver, accounts['Paidviewpoint'], book)
    runPinecone(driver, accounts['Pinecone'], book)
    # runInboxDollars(driver, accounts['InboxDollars'], book)
    runSwagbucks(driver, dailyGame, accounts['Swagbucks'], book)
    runMyPoints(driver, accounts['MyPoints'], book)
    driver.closeWindowsExcept([':8000/'])
    driver.findWindowByUrl("/scripts/daily")
    return True
    
if __name__ == '__main__':
    driver = WebDriver("Chrome")
    personalBook = GnuCash('Finance')
    accounts = getDailyMRAccounts(personalBook)
    runDailyMR(driver, accounts, personalBook, False)
    personalBook.closeBook()

    