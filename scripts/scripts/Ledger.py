import os

if __name__ == '__main__' or __name__ == "Ledger":
    from Classes.Asset import Crypto
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, isProcessRunning
else:
    from .Classes.Asset import Crypto
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, isProcessRunning

def getLedgerAccounts(readBook):
    Bitcoin = Crypto("Bitcoin", readBook)
    Ethereum = Crypto("Ethereum", readBook)
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
    book = GnuCash('Finance')    
    coinList = getLedgerAccounts(book)
    runLedger(coinList, book)
    for coin in coinList:
        coin.getData()
    book.closeBook()
    