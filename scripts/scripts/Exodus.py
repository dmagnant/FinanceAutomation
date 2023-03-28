if __name__ == '__main__' or __name__ == "Exodus":
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage    
    from Functions.GnuCashFunctions import openGnuCashBook       
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import openGnuCashBook
    
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
    book = openGnuCashBook('Finance', False, False)
    Cosmos = Crypto("Cosmos", book)
    runExodus(Cosmos, book)
    Cosmos.getData()
    if not book.is_saved:
        book.save()
    book.close()
