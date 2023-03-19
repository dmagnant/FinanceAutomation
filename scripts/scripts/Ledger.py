import os

if __name__ == '__main__' or __name__ == "Ledger":
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage, isProcessRunning
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage, isProcessRunning

def getLedgerAccounts():
    Bitcoin = Crypto("Bitcoin")
    Ethereum = Crypto("Ethereum", "ETH-Ledger")
    Cosmos = Crypto("Cosmos")
    Polkadot = Crypto("Polkadot")
    Algorand = Crypto("Algorand")
    return [Bitcoin, Ethereum, Cosmos, Polkadot, Algorand]

def updateCoin(coin):
    balance = float(input(f"Paste {coin.symbol} balance here: "))
    coin.setBalance(balance)
    coin.setPrice(coin.getPriceFromCoinGecko())
    coin.updateSpreadsheetAndGnuCash()
    
def runLedger(coinList):
    if not (isProcessRunning('Ledger Live.exe')):
        os.startfile(r'C:\Program Files\Ledger Live\Ledger Live.exe')
    showMessage('Open Ledger and Verify Balances', "click OK and follow prompts")
    for coin in coinList:
        updateCoin(coin)

if __name__ == '__main__':
    coinList = getLedgerAccounts()
    runLedger(coinList)
    for coin in coinList:
        coin.getData()
