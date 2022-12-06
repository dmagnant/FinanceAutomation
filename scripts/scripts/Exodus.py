if __name__ == '__main__' or __name__ == "Exodus":
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage    
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage
    
def runExodus():
    Cosmos = Crypto("Cosmos")
    showMessage('Cosmos (ATOM) balance via Exodus',"Open Exodus Desktop \n"
                                "Rewards > Cosmos > Claim Reward > Claim Reward \n"
                                "Earn Atom > Stake All \n"
                                "Overview > Copy Staking Balance \n"
                                "After clicking OK, paste into python window \n")
    atomBalance = float(input("Paste ATOM balance here: ").replace(Cosmos.symbol, ''))
    Cosmos.setBalance(atomBalance)
    Cosmos.setPrice(Cosmos.getPriceFromCoinGecko())
    Cosmos.updateSpreadsheetAndGnuCash()
    return [Cosmos]

if __name__ == '__main__':
    response = runExodus()
    for coin in response:
        coin.getData()
