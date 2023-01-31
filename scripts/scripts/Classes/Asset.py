from datetime import datetime
from decimal import Decimal

from piecash import Split, Transaction

if __name__ == "Classes.Asset":
    from Functions.GeneralFunctions import getCryptocurrencyPrice
    from Functions.GnuCashFunctions import (getAccountPath, getGnuCashBalance,
                                            openGnuCashBook,
                                            updateCryptoPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
else:
    from scripts.scripts.Functions.GeneralFunctions import (
        getCryptocurrencyPrice)
    from scripts.scripts.Functions.GnuCashFunctions import (
        getAccountPath, getGnuCashBalance, openGnuCashBook,
        updateCryptoPriceInGnucash)
    from scripts.scripts.Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet

def getCryptoSymbolByName(self):
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
                print(f'Cryptocurrency: {self.name} not found in "getCryptoSymbolByName" function')
                
def updateCoinQuantityFromStakingInGnuCash(self):
        myBook = openGnuCashBook('Finance', False, False)
        coinDifference = Decimal(self.balance) - Decimal(self.gnuBalance)
        if coinDifference > 0:
            with myBook:
                split = [Split(value=-0, memo="scripted", account=myBook.accounts(fullname='Income:Investments:Staking')),
                        Split(value=0, quantity=round(Decimal(coinDifference), 6), memo="scripted", account=myBook.accounts(fullname=self.gnuAccount))]
                Transaction(post_date=datetime.today().date(), currency=myBook.currencies(mnemonic="USD"), description=self.symbol + ' staking', splits=split)
                myBook.save()
                myBook.flush()
            myBook.close()
        elif coinDifference < 0:
            print(f'given balance of {self.balance} {self.symbol} '
            f'minus gnuCash balance of {self.gnuBalance} '
            f'leaves unexpected coin difference of {coinDifference} '
            f'is it rounding issue?')                

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

    def setGnuAccount(self, account):
        self.gnuAccount = getAccountPath(account)
    
    def getGnuBalance(self):
        return self.gnuBalance
    
    def updateGnuBalance(self, myBook):
        self.gnuBalance = getGnuCashBalance(myBook, self.gnuAccount)

class Crypto(Asset):
    "this is a class for tracking cryptocurrency information"
    def __init__(self, name, account=None):
        self.name = name
        self.lowerName = name.lower()
        self.balance = None
        self.price = None
        self.account = account
        self.symbol = getCryptoSymbolByName(self)
        self.gnuAccount = getAccountPath(self.name, self.account)
        self.gnuBalance = getGnuCashBalance(openGnuCashBook('Finance', True, True), self.gnuAccount)
                
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
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 2, self.price, self.symbol)
        updateCoinQuantityFromStakingInGnuCash(self)

    def updateBalanceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 1, self.balance, self.symbol)

    def updatePriceInSpreadSheet(self, account=None):
        account = self.symbol if account == None else account
        updateSpreadsheet('Asset Allocation', 'Cryptocurrency', account, 2, self.price, self.symbol)

    def updateBalanceInGnuCash(self, account=None):
        account = self.symbol if account == None else account
        updateCoinQuantityFromStakingInGnuCash(self)

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
        book = 'Home' if (self.name == 'Ally' or self.name == 'BoA-joint') else 'Finance'
        self.gnuBalance = getGnuCashBalance(openGnuCashBook(book, True, True), self.gnuAccount)
    
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
        today = datetime.today()
        month = today.month
        year = today.year
        # switch worksheets if running in December (to next year's worksheet)
        if month == 12:
            year = year + 1
        if self.name == 'BoA-joint':
            openSpreadsheet(driver, 'Home', '2023 Balance')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC', True)
        else:
            openSpreadsheet(driver, 'Checking Balance', '2023')
            updateSpreadsheet('Checking Balance', year, self.name, month, balance, self.name + " CC")
            updateSpreadsheet('Checking Balance', year, self.name, month, balance, self.name + " CC", True)
            