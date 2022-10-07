if __name__ == '__main__' or __name__ == "IoPay":
    from Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet
else:
    from .Functions.GeneralFunctions import (setDirectory, showMessage, getCryptocurrencyPrice)
    from .Functions.GnuCashFunctions import (updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash)
    from .Functions.SpreadsheetFunctions import updateSpreadsheet


def runIoPay():
    directory = setDirectory()
    showMessage('IOTX balance via IoPay Desktop',"Open IoPay Desktop and Connect Ledger \n"
                                "Connect Ledger > Unlock > Stake your tokens (launches webpage) \n"
                                "My Stakes > Action > Add Stake \n"
                                "stake available balance (may need 100 minimum) \n"
                                "After clicking OK, see python window for inputs \n")
    walletBalance = float(input("copy WALLET BALANCE and paste here:  \n").replace(" IOTX", ""))
    stakedBalance = float(input("copy TOTAL STAKED AMOUNT and paste here:  \n").replace(" IOTX", "").replace(",",''))
    iotxBalance = walletBalance + stakedBalance
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'IOTX', 1, iotxBalance, "IOTX")
    updateCoinQuantityFromStakingInGnuCash(iotxBalance, 'IOTX')
    iotxPrice = getCryptocurrencyPrice('iotex')['iotex']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'IOTX', 2, iotxPrice, "IOTX")
    updateCryptoPriceInGnucash('IOTX', format(iotxPrice, ".2f"))

    return iotxBalance

if __name__ == '__main__':
    response = runIoPay()
    print('balance: ' + str(response))
