if __name__ == '__main__' or __name__ == "Daily_MR":
    from AmazonGC import confirmAmazonGCBalance
    from Bing import runBing
    from Classes.WebDriver import Driver
    from Pinecone import runPinecone
    from Presearch import searchUsingPresearch
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
else:
    from .AmazonGC import confirmAmazonGCBalance
    from .Bing import runBing
    from .Classes.WebDriver import Driver
    from .Pinecone import runPinecone
    from .Presearch import searchUsingPresearch
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut

def runDailyMR():
    driver1 = Driver("Edge", False)
    runBing(driver1.webDriver)
    driver1.webDriver.quit()
    driver = Driver("Chrome")    
    searchUsingPresearch(driver)
    runTellwut(driver)
    confirmAmazonGCBalance(driver)
    runPinecone(driver)
    searchUsingPresearch(driver)
    runSwagbucks(driver, True)
    
if __name__ == '__main__':
    runDailyMR()