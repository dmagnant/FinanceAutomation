if __name__ == '__main__' or __name__ == "Exodus":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from .Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet

def runExodus():
    directory = setDirectory()
    showMessage('Cosmos (ATOM) balance via Exodus',"Open Exodus Desktop \n"
                                "Rewards > Cosmos > Claim Reward > Claim Reward \n"
                                "Earn Atom > Stake All \n"
                                "Overview > Copy Staking Balance \n"
                                "After clicking OK, paste into python window \n")
    atomBalance = float(input("Paste ATOM balance here: ").replace('ATOM', ''))
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ATOM', 1, atomBalance, "ATOM")
    updateCoinQuantityFromStakingInGnuCash(atomBalance, 'ATOM')
    atomPrice = getCryptocurrencyPrice('cosmos')['cosmos']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ATOM', 2, atomPrice, "ATOM")
    updateCryptoPriceInGnucash('ATOM', format(atomPrice, ".2f"))
    
    showMessage('Algorand (ALGO) balance via Exodus',"Open Exodus Desktop \n"
                                "Rewards > ALGO > Claim \n"
                                "Copy Available Balance \n"
                                "After clicking OK, paste into python window \n")
                                
    algoBalance = float(input("Paste ALGO balance here: ").replace('ALGO', ''))
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ALGO', 1, algoBalance, "ALGO")
    updateCoinQuantityFromStakingInGnuCash(algoBalance, 'ALGO')
    algoPrice = getCryptocurrencyPrice('algorand')['algorand']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'ALGO', 2, algoPrice, "ALGO")
    updateCryptoPriceInGnucash('ALGO', format(algoPrice, ".2f"))
    return [atomBalance, algoBalance]

if __name__ == '__main__':
    response = runExodus()
    print('atom balance: ' + response[0])
    print('algo balance: ' + response[1])
