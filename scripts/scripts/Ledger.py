import os

if __name__ == '__main__' or __name__ == "Ledger":
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage, isProcessRunning
    from Functions.GnuCashFunctions import openGnuCashBook       
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage, isProcessRunning
    from .Functions.GnuCashFunctions import openGnuCashBook   

def getLedgerAccounts(readBook):
    Bitcoin = Crypto("Bitcoin", readBook)
    Ethereum = Crypto("Ethereum", readBook, "ETH-Ledger")
    Cosmos = Crypto("Cosmos", readBook)
    Polkadot = Crypto("Polkadot", readBook)
    Algorand = Crypto("Algorand", readBook)
    return [Bitcoin, Ethereum, Cosmos, Polkadot, Algorand]

def updateCoin(coin, book):
    balance = float(input(f"Paste {coin.symbol} balance here: "))
    coin.setBalance(balance)
    coin.setPrice(coin.getPriceFromCoinGecko())
    coin.updateSpreadsheetAndGnuCash(book)
    
def runLedger(coinList, book):
    if not (isProcessRunning('Ledger Live.exe')):
        os.startfile(r'C:\Program Files\Ledger Live\Ledger Live.exe')
    showMessage('Open Ledger and Verify Balances', "click OK and follow prompts")
    for coin in coinList:
        updateCoin(coin, book)

if __name__ == '__main__':
    book = openGnuCashBook('Finance', False, False)
    coinList = getLedgerAccounts(book)
    runLedger(coinList, book)
    for coin in coinList:
        coin.getData()
    if not book.is_saved:
        book.save()
    book.close()
    