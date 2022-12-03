if __name__ == "Classes.Asset":
    from Functions.GeneralFunctions import getCryptocurrencyPrice, setDirectory
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash
else:
    from scripts.scripts.Functions.GeneralFunctions import getCryptocurrencyPrice, setDirectory
    from scripts.scripts.Functions.SpreadsheetFunctions import updateSpreadsheet
    from scripts.scripts.Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash

def getCryptoSymbolByName(name):
    match name.lower():
        case "algorand":
            return 'ALGO'
        case "bitcoin":
            return 'BTC'
        case "cardano":
            return 'ADA'
        case "cosmos":
            return 'ATOM'
        case "ethereum":
            return 'ETH'
        case "ethereum2":
            return 'ETH2'
        case "iotex":
            return 'IOTX'
        case "loopring":
            return 'LRC'
        case "polkadot":
            return 'DOT'
        case "presearch":
            return 'PRE'
        case _:
            print(f'Cryptocurrency: {name} not found in "getCryptoSymbolByName" function')
    
class Asset(object):
    "this is a class for tracking asset information"
    def getName(self):
        return self.name
    
    def getBalance(self):
        return self.balance
        
    def setBalance(self, balance):
        self.balance = balance

class Crypto(Asset):
    "this is a class for tracking cryptocurrency information"
    def __init__(self, name):
        self.name = name
        self.lowerName = name.lower()
        self.balance = None
        self.price = None
        self.symbol = getCryptoSymbolByName(name)
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'symbol: {self.symbol} \n'
                f'balance: {self.balance} \n'
                f'price: {self.price}')
        
    def getPrice(self):
        return self.price
        
    def getPriceFromCoinGecko(self):
        return getCryptocurrencyPrice(self.name)[self.lowerName]['usd']
        
    def setPrice(self, price):
        self.price = price
        
    def getSymbol(self):
        return self.symbol
    
    def updateSpreadsheetAndGnuCash(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet(setDirectory(), 'Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)
        updateSpreadsheet(setDirectory(), 'Asset Allocation', 'Cryptocurrency', account, 2, self.price, self.symbol)
        updateCoinQuantityFromStakingInGnuCash(self.balance, account)
        updateCryptoPriceInGnucash(self.symbol, format(self.price, ".2f"))        

    def updateBalanceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet(setDirectory(), 'Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)

    def updatePriceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet(setDirectory(), 'Asset Allocation', 'Cryptocurrency', account, 2, self.price, self.symbol)

    def updateBalanceInGnuCash(self, account=None):
        account = self.symbol if account == None else account
        updateCoinQuantityFromStakingInGnuCash(self.balance, account)

    def updatePriceInGnuCash(self, account=None):
        account = self.symbol if account == None else account
        updateCryptoPriceInGnucash(self.symbol, format(self.price, ".2f"))
        
class USD(Asset):
    "this is a class for tracking USD information"
    def __init__(self, name):
        self.name = name
        self.lowerName = name.lower()
        self.balance = None
        self.currency = 'USD'
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'balance: ${self.balance}')
