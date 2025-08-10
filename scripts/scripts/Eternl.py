import time, json

if __name__ == '__main__' or __name__ == "Eternl":
    from Classes.Asset import Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getNotes
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getNotes

def locateEternlWindow(driver):
    found = driver.findWindowByUrl("eternl.io/mainnet/wallet/home")
    if not found:   eternlLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def eternlLogin(driver):
    driver.openNewWindow('https://eternl.io/landing/login')
    driver.getElementAndSendKeys('xpath', "//*[@id='inputPinConfirm1']", str(json.loads(getNotes('Eternl'))['LoginCode'])) # PIN code
    time.sleep(1)

def getEternlBalance(driver):
    locateEternlWindow(driver)
    rawBalance = driver.getElementText('xpath', "//*[@id='eternl-app']/div[2]/div[1]/div/div[1]/div[1]/div/div/div/div[1]/button/div[2]/div/div[2]/div[1]/div")
    if rawBalance:
        balance = float(rawBalance.replace('\n', '').replace('₳','').replace(',', ''))
        return balance
    return rawBalance

def runEternl(driver, account, book, spreadsheet):
    account.setBalance(getEternlBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(spreadsheet, book)
    
# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     Cardano = Security("Cardano", book)    
#     runEternl(driver, Cardano, book)
#     Cardano.getData()
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateEternlWindow(driver)
    balance = getEternlBalance(driver)
    print(balance)
