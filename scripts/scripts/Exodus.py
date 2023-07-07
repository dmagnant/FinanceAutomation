if __name__ == '__main__' or __name__ == "Exodus":
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage    
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage
    
def runExodus(account, book):
    showMessage('Cosmos (ATOM) balance via Exodus',"Open Exodus Desktop \n"
                                "Rewards > Cosmos > Claim Reward > Claim Reward \n"
                                "Earn Atom > Stake All \n"
                                "Overview > Copy Staking Balance \n"
                                "After clicking OK, paste into python window \n")
    atomBalance = float(input("Paste ATOM balance here: ").replace(account.symbol, ''))
    account.setBalance(atomBalance)
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)

if __name__ == '__main__':
    book = GnuCash('Finance')    
    Cosmos = Security("Cosmos", book)
    runExodus(Cosmos, book)
    Cosmos.getData()
    book.closeBook()
