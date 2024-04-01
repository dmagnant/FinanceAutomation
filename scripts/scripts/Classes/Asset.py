from datetime import datetime
from decimal import Decimal

if __name__ == "Classes.Asset":
    from Functions.GeneralFunctions import getCryptocurrencyPrice, getAccountPath
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateCheckingBalanceSpreadsheet
else:
    from scripts.scripts.Functions.GeneralFunctions import getCryptocurrencyPrice, getAccountPath
    from scripts.scripts.Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet, updateCheckingBalanceSpreadsheet

def getSymbolByName(self):
    match self.name.lower():
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
        case 'eth-ledger':
            return 'ETH'
        case 'he investment':
            return "VIIIX"        
        case 'optum investment':
            return "VFIAX"
        case "iotex":
            return 'IOTX'
        case "loopring":
            return 'LRC'
        case "polkadot":
            return 'DOT'
        case "presearch":
            return 'PRE'
        case 'ripple':
            return 'XRP'
        case "bing":
            return 'BNG'
        case "pinecone":
            return 'PNCN'
        case "tellwut":
            return 'TWT'
        case "swagbucks":
            return 'SB'
        case 'employee benefit index':
            return 'M038'
        case 'total stock market(401k)':
            return '8585'
        case 'ira vti' | 'roth ira vti':
            return 'VTI'      
        case 'ira vxus' | 'roth ira vxus':
            return 'VXUS'        
        case 'ira spaxx' | 'roth ira spaxx' | 'brokerage spaxx':
            return 'SPAXX'
        case _:
            print(f'Security: {self.name} not found in "getSymbolByName" function')

def updateCoinQuantityFromStakingInGnuCash(self, myBook):
    # myBook = myBook.getWriteBook()
    coinDifference = Decimal(self.balance) - Decimal(self.gnuBalance)
    amount = round(self.price * coinDifference, 3)
    if coinDifference > 0.001:
        transactionInfo = {'amount': amount, 'toAccount': self.gnuAccount, 'coinDifference': round(Decimal(coinDifference), 6), 'description': self.symbol + ' staking'}
        myBook.writeStakingTransaction(transactionInfo)
    elif coinDifference < 0:
        print(f'given balance of {self.balance} {self.symbol} '
        f'minus gnuCash balance of {self.gnuBalance} '
        f'leaves unexpected coin difference of {coinDifference} '
        f'is it rounding issue?')                

class Asset:
    "this is a class for tracking asset information"
    def getName(self):
        return self.name
    
    def getBalance(self):
        return self.balance
    
    def setBalance(self, balance):
        self.balance = balance
    
    def getGnuAccount(self):
        return self.gnuAccount

    def setGnuAccount(self):
        self.gnuAccount = getAccountPath(self)
    
    def getGnuBalance(self):
        return self.gnuBalance
    

        
class Security(Asset):    # this is a class for tracking security information
    def __init__(self, name, book, account=None):
        self.name = name
        self.balance = ''
        self.value = ''
        self.account = account
        self.symbol = getSymbolByName(self)
        self.price = book.getPriceInGnucash(self.symbol, datetime.today().date())
        self.gnuAccount = getAccountPath(self)
        self.gnuBalance = Decimal(book.getBalance(self.gnuAccount))
        self.gnuValue = self.getGnuValue()
    
    def getGnuValue(self):
        price = Decimal(self.price)
        return round(self.gnuBalance * price, 2) if float(self.gnuBalance * price)>0 else 0
    
    def updateGnuBalanceAndValue(self, balance):
        self.gnuBalance = Decimal(balance)
        self.gnuValue = self.getGnuValue()
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'symbol: {self.symbol} \n'
                f'balance: {self.balance} \n'
                f'gnuBalance: {self.gnuBalance} \n'
                f'price: {self.price}')
        
    def getPrice(self):
        return self.price
        
    def getPriceFromCoinGecko(self):
        return getCryptocurrencyPrice(self.name)[self.name.lower()]['usd']
        
    def setPrice(self, price):
        self.price = Decimal(price)
        
    def getSymbol(self):
        return self.symbol
    
    def updateSpreadsheetAndGnuCash(self, book):
        account = self.symbol if self.account == None else self.account
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 2, float(self.price), self.symbol)
        updateCoinQuantityFromStakingInGnuCash(self, book)
        self.updateGnuBalance(book.getBalance(self.gnuAccount))

    def updateBalanceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)

    def updatePriceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 2, self.price, self.symbol)

    def updateBalanceInGnuCash(self, book, account=None):
        account = self.symbol if account == None else account
        updateCoinQuantityFromStakingInGnuCash(self, book)

    def updateGnuBalance(self, balance):
        self.gnuBalance = Decimal(balance)

class USD(Asset):
    "this is a class for tracking USD information"
    def __init__(self, name, book):
        self.name = name
        self.balance = ""
        self.units = 0
        self.currency = 'USD'
        self.reviewTransactions = []
        self.account = None
        self.gnuAccount = getAccountPath(self)
        balance = book.getBalance(self.gnuAccount)
        self.gnuBalance = round(balance, 2) if float(balance)>0 else 0
    
    def updateGnuBalance(self, balance):
        self.gnuBalance = round(Decimal(balance), 2)
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'   balance: ${self.balance} \n'
                f'gnuBalance: ${self.gnuBalance}')
        if self.reviewTransactions:
            print(
                f'Review Transactions: \n'
                f'{self.reviewTransactions}')

    def getReviewTransactions(self):
        return self.reviewTransactions

    def setReviewTransactions(self, transactions):
        self.reviewTransactions.append(transactions)
    
    def locateAndUpdateSpreadsheet(self, driver):
        balance = 0.00 if float(self.balance) < 0 else float(self.balance) * -1
        today = datetime.today()
        month = today.month
        year = today.year
        # switch worksheets if running in December (to next year's worksheet)
        if month == 12:
            year = year + 1
        if self.name == 'BoA-joint':
            openSpreadsheet(driver, 'Home', str(year) + ' Balance')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC', True)
        else:
            openSpreadsheet(driver, 'Checking Balance', str(year))
            updateCheckingBalanceSpreadsheet('Checking Balance', year, self.name, month, balance, self.name + " CC")
    

            