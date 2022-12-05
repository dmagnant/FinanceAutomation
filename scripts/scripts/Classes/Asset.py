from datetime import datetime

if __name__ == "Classes.Asset":
    from Functions.GeneralFunctions import getCryptocurrencyPrice, setDirectory
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash, openGnuCashBook
else:
    from scripts.scripts.Functions.GeneralFunctions import getCryptocurrencyPrice, setDirectory
    from scripts.scripts.Functions.SpreadsheetFunctions import updateSpreadsheet
    from scripts.scripts.Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash, openGnuCashBook

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

def getGnuCashBalance(myBook, account):
    with myBook as book:
        balance = book.accounts(fullname=account).get_balance()
    book.close()
    return balance

def getAccountPath(account):
    match account:
        case 'ADA':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano"            
        case 'ALGO':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Algorand"
        case 'Ally':
            return "Assets:Ally Checking Account"
        case 'AmazonGC':
            return "Assets:Liquid Assets:Amazon GC"
        case 'Amex':
            return "Liabilities:Credit Cards:Amex BlueCash Everyday"
        case 'ATOM':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cosmos"                  
        case 'Barclays':
            return "Liabilities:Credit Cards:BarclayCard CashForward"
        case 'BTC':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin"                
        case 'BTC-Midas':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin:BTC-Midas"
        case 'BTC-MyConstant':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Bitcoin:BTC-MyConstant"                
        case 'BoA':
            return "Liabilities:Credit Cards:BankAmericard Cash Rewards"
        case 'BoA-joint':
            return "Liabilities:BoA Credit Card"
        case 'Bonds':
            return "Assets:Liquid Assets:Bonds"
        case 'Chase':
            return "Liabilities:Credit Cards:Chase Freedom"
        case 'Crypto':
            return "Assets:Non-Liquid Assets:CryptoCurrency"
        case 'Discover':
            return "Liabilities:Credit Cards:Discover It"
        case 'DOT':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Polkadot"
        case 'ETH':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum"
        case 'ETH-Kraken':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Kraken"
        case 'ETH-Midas':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Midas"
        case 'ETH-MyConstant':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-MyConstant"
        case 'ETH2':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum2"
        case 'HSA':
            return "Assets:Non-Liquid Assets:HSA:NM HSA"
        case 'IOTX':
            return "Assets:Non-Liquid Assets:CryptoCurrency:IoTex"
        case 'Liquid Assets':
            return "Assets:Liquid Assets"            
        case 'MyConstant':
            return "Assets:Liquid Assets:Bonds:My Constant"
        case 'PRE':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Presearch"
        case 'Checking':
            return "Assets:Liquid Assets:Sofi:Checking"
        case 'Savings':
            return "Assets:Liquid Assets:Sofi:Savings"                
        case 'TIAA':
            return "Assets:Liquid Assets:TIAA"
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Bonds:Worthy Bonds"
        case _:
            print(f'account: {account} not found in "getAccountPath" function')

class Asset(object):
    "this is a class for tracking asset information"
    def getName(self):
        return self.name
    
    def getBalance(self):
        return self.balance
    
    def setBalance(self, balance):
        self.balance = balance
    
    def getGnuAccount(self):
        return self.gnuAccount
    
    def getGnuBalance(self):
        return self.gnuBalance
    
    def updateGnuBalance(self, myBook):
        self.gnuBalance = getGnuCashBalance(myBook, self.gnuAccount)
    
class Crypto(Asset):
    "this is a class for tracking cryptocurrency information"
    def __init__(self, name):
        self.name = name
        self.lowerName = name.lower()
        self.balance = None
        self.price = None
        self.symbol = getCryptoSymbolByName(name)
        self.gnuAccount = getAccountPath(self.name)        
    
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
        self.reviewTransactions = None
        self.gnuAccount = getAccountPath(self.name)
        if name == 'Ally' or name == 'BoA-joint': # or BoA joint
            myBook = openGnuCashBook('Home', True, True)
        else:
            myBook = openGnuCashBook('Finance', False, False)
        self.gnuBalance = getGnuCashBalance(myBook, self.gnuAccount)
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'   balance: ${self.balance} \n'
                f'gnuBalance: ${self.gnuBalance} \n'
                f'Review Transactions: \n'
                f'{self.reviewTransactions}')

    def getReviewTransactions(self):
        return self.reviewTransactions

    def setReviewTransactions(self, transactions):
        self.reviewTransactions = transactions
    
    def locateAndUpdateSpreadsheet(self, driver):
        balance = 0.00 if float(self.balance) < 0 else float(self.balance) * -1
        directory = setDirectory()
        today = datetime.today()
        month = today.month
        year = today.year
        # switch worksheets if running in December (to next year's worksheet)
        if month == 12:
            year = year + 1
        if self.name == 'BoA-joint':
            updateSpreadsheet(directory, 'Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC')
            updateSpreadsheet(directory, 'Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC', True)
            # Display Home spreadsheet
            driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/edit#gid=317262693');")
        else:
            updateSpreadsheet(directory, 'Checking Balance', year, self.name, month, balance, self.name + " CC")
            updateSpreadsheet(directory, 'Checking Balance', year, self.name, month, balance, self.name + " CC", True)
            # Display Checking Balance spreadsheet
            driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=1688093622');")
