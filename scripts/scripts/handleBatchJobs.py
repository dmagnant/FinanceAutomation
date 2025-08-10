import sys, time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, NoSuchWindowException

if __name__ == '__main__' or __name__ == "handleBatchJobs":
    from DailyMR import getDailyMRAccounts, runDailyMR
    from DailyBank import getDailyBankAccounts, runDailyBank
    from Tellwut import runTellwut
    from Swagbucks import runSwagbucks
    from InboxDollars import runInboxDollars
    from Functions.GeneralFunctions import setDirectory, getStartAndEndOfDateRange, getLogger
    from Classes.GnuCash import GnuCash
    from Classes.WebDriver import Driver
    from Classes.Asset import USD, Security

def runScripts(scripts, log=getLogger()):
    book = GnuCash('Finance')
    driver = Driver("Chrome")
    results = {}
    for script in scripts:
        log.info(f'Running script: {script}')
        scriptResult = False
        try:
            if script == 'DailyMR':
                accounts = getDailyMRAccounts(book)
                if runDailyMR(accounts, book, runAlu=True):
                    scriptResult = True
            elif script == 'Tellwut':
                if runTellwut(driver, Security("Tellwut", book), book):
                    scriptResult = True
            elif script == 'Swagbucks':
                if runSwagbucks(driver, True, Security("Swagbucks", book), book, runSearch=True):
                    scriptResult = True
            elif script == 'DailyBank':
                jointBook = GnuCash('Home')
                accounts = getDailyBankAccounts(book, jointBook)
                dateRange = getStartAndEndOfDateRange(timeSpan=7)
                gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
                if runDailyBank(accounts, book, jointBook, gnuCashTransactions, dateRange):
                    scriptResult = True
            elif script == 'InboxDollars':
                if runInboxDollars(driver, USD("InboxDollars", book), book):
                    scriptResult = True
            elif script == 'Test':
                driver.openNewWindow("http://127.0.0.1:8000/scripts/tellwut")
                if driver.getElementAndClick('xpath', '/html/body/div[1]/div/div[1]/form/button[1]'):
                    time.sleep(1)
                    log.info('started script via click')
                    scriptResult = True
                driver.webDriver.quit()
            else:
                log.warning(f'No script found for {script}')
        except (WebDriverException, NoSuchWindowException) as e:
            log.error(f"WebDriver error: {e}")
        if scriptResult:
            log.info(f'Successfully ran script: {script}')
            results[script] = 'Success'
        else:
            log.error(f'Failed to run script: {script}')
            results[script] = 'Failed'
    book.closeBook()
    return results

if __name__ == '__main__':
    scripts = sys.argv
    scripts.remove(sys.argv[0])
    log = getLogger()
    log.info(f'Starting batch job {scripts}')
    if len(scripts) > 0:
        runScripts(scripts, log)
    else:
        log.error('No scripts provided to run')

