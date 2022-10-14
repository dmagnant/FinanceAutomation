if __name__ == '__main__' or __name__ == "Daily_MR":
    from Functions.WebDriverFunctions import openWebDriver
    from AmazonGC import confirmAmazonGCBalance
    from Bing import runBing
    from Pinecone import runPinecone
    from Presearch import searchUsingPresearch
    from Swagbucks import runSwagbucks
    from Tellwut import runTellwut
else:
    from .Functions.WebDriverFunctions import openWebDriver
    from .AmazonGC import confirmAmazonGCBalance
    from .Bing import runBing
    from .Pinecone import runPinecone
    from .Presearch import searchUsingPresearch
    from .Swagbucks import runSwagbucks
    from .Tellwut import runTellwut

def runDailyMR():
    driver1 = openWebDriver("Edge", False)
    runBing(driver1)
    driver1.quit()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    searchUsingPresearch(driver)
    runTellwut(driver)
    confirmAmazonGCBalance(driver)
    runPinecone(driver)
    searchUsingPresearch(driver)
    runSwagbucks(driver, True)
    
if __name__ == '__main__':
    runDailyMR()