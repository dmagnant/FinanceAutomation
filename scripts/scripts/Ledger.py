import os

if __name__ == '__main__' or __name__ == "Ledger":
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, isProcessRunning
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, isProcessRunning

def getLedgerAccounts(readBook):
    Bitcoin = Security("Bitcoin", readBook)
    Ethereum = Security("Ethereum", readBook)
    Cosmos = Security("Cosmos", readBook)
    Polkadot = Security("Polkadot", readBook)
    Algorand = Security("Algorand", readBook)
    XRP = Security("Ripple", readBook)
    return [Bitcoin, Ethereum, Cosmos, Polkadot, Algorand, XRP]

def updateCoin(coin, book):
    balance = float(input(f"Paste {coin.symbol} balance here: "))
    coin.setBalance(balance)
    coin.setPrice(coin.getPriceFromCoinGecko())
    coin.updateSpreadsheetAndGnuCash(book)
    
def runLedger(coinList, book):
    if not (isProcessRunning('Ledger Live.exe')):   os.startfile(r'C:\Program Files\Ledger Live\Ledger Live.exe')
    showMessage('Open Ledger and Verify Balances', "click OK and follow prompts")
    for coin in coinList:   updateCoin(coin, book)

# if __name__ == '__main__':
#     book = GnuCash('Finance')    
#     coinList = getLedgerAccounts(book)
#     runLedger(coinList, book)
#     for coin in coinList:
#         coin.getData()
#     book.closeBook()


if __name__ == '__main__':
    book = GnuCash('Finance')
    gnuAccount = 'Assets:Non-Liquid Assets:CryptoCurrency'
    from datetime import datetime
    date = date=datetime.today().date().replace(month=3, day=31)
    print(book.getBalance(gnuAccount, date))


