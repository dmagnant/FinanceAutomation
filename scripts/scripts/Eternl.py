import time

if __name__ == '__main__' or __name__ == "Eternl":
    from Classes.Asset import Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash

def locateEternlWindow(driver):
    found = driver.findWindowByUrl("eternl.io/app/mainnet")
    if not found:   eternlLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def eternlLogin(driver):
    driver.openNewWindow('https://eternl.io/app/mainnet/wallet/xpub1wxalshqc32m-ml/summary')
    time.sleep(1)
    
def getEternlBalance(driver):
    locateEternlWindow(driver)
    while True:
        rawStatus = driver.getElementText('xpath', "//*[@id='cc-main-container']/div/div[3]/div[2]/nav/div/div[2]/div/div/div[1]/div[2]/div/span", wait=2)
        if rawStatus:
            status = rawStatus.replace('\n', '')
            print(status)
            if 'initializing' in status or 'Syncing' in status:
                time.sleep(2)
                driver.webDriver.refresh()
                time.sleep(2)
            else:                          
                break
    rawBalance = driver.getElementText('xpath', "//*[@id='cc-main-container']/div/div[3]/div[2]/nav/div/div[2]/div/div/div[1]/div[2]/div/div", allowFail=False)
    if rawBalance:
        balance = float(rawBalance.replace('\n', '').replace('₳','').replace(',', ''))
        return balance + float(2618.232158) # balance current in Kraken
    return rawBalance

def runEternl(driver, account, book, spreadsheet):
    account.setBalance(getEternlBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(spreadsheet, book)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Cardano = Security("Cardano", book)    
    runEternl(driver, Cardano, book)
    Cardano.getData()
    book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateEternlWindow(driver)
                                         
    driver.webDriver.refresh()