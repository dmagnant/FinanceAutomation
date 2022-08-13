from Functions.Functions import (getCryptocurrencyPrice, setDirectory, showMessage,
                       updateCoinQuantityFromStakingInGnuCash,
                       updateCryptoPriceInGnucash, updateSpreadsheet)


def runExodus(directory):
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

    return atomBalance

if __name__ == '__main__':
    directory = setDirectory()
    response = runExodus(directory)
    print('balance: ' + response)
