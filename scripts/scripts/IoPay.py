if __name__ == '__main__' or __name__ == "Exodus":
    from Functions.GeneralFunctions import showMessage
    from Classes.Asset import Crypto    
else:
    from .Functions.GeneralFunctions import showMessage
    from .Classes.Asset import Crypto    

def runIoPay():
    IoTex = Crypto("IoTex")
    showMessage('IOTX balance via IoPay Desktop',"Open IoPay Desktop and Connect Ledger \n"
                                "Connect Ledger > Unlock > Stake your tokens (launches webpage) \n"
                                "My Stakes > Action > Add Stake \n"
                                "stake available balance (may need 100 minimum) \n"
                                "After clicking OK, see python window for inputs \n")
    walletBalance = float(input("copy WALLET BALANCE and paste here:  \n").replace(" IOTX", ""))
    stakedBalance = float(input("copy TOTAL STAKED AMOUNT and paste here:  \n").replace(" IOTX", "").replace(",",''))
    iotxBalance = walletBalance + stakedBalance
    IoTex.setBalance(iotxBalance)
    IoTex.setPrice(IoTex.getPriceFromCoinGecko())
    IoTex.updateSpreadsheetAndGnuCash()
    return iotxBalance

if __name__ == '__main__':
    response = runIoPay()
    for coin in response:
        coin.getData()

