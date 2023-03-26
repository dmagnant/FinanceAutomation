from datetime import datetime
from decimal import Decimal

from piecash import Split, Transaction

if __name__ == "Classes.Asset":
    from Functions.GeneralFunctions import getCryptocurrencyPrice
    from Functions.GnuCashFunctions import (getAccountPath, getGnuCashBalance,
                                            openGnuCashBook,
                                            updatePriceInGnucash, getPriceInGnucash)
    from Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
elif __name__ == 'scripts.Classes.Asset':
    from scripts.Functions.GeneralFunctions import (
        getCryptocurrencyPrice)
    from scripts.Functions.GnuCashFunctions import (
        getAccountPath, getGnuCashBalance, openGnuCashBook,
        updatePriceInGnucash, getPriceInGnucash)
    from scripts.Functions.SpreadsheetFunctions import updateSpreadsheet, openSpreadsheet
else:
    from scripts.scripts.Functions.GeneralFunctions import (
        getCryptocurrencyPrice)
    from scripts.scripts.Functions.GnuCashFunctions import (
        getAccountPath, getGnuCashBalance, openGnuCashBook,
        updatePriceInGnucash, getPriceInGnucash)
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
        case "bing":
            return 'BNG'
        case "pinecone":
            return 'PNCN'
        case "tellwut":
            return 'TWT'
        case "swagbucks":
            return 'SB'
        case _:
            print(f'Cryptocurrency: {self.name} not found in "getCryptoSymbolByName" function')
                
def updateCoinQuantityFromStakingInGnuCash(self):
        myBook = openGnuCashBook('Finance', False, False)
        coinDifference = Decimal(self.balance) - Decimal(self.gnuBalance)
        if coinDifference > 0.001:
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
        self.gnuBalance = round(Decimal(getGnuCashBalance(myBook, self.gnuAccount)), 2)
        
class Crypto(Asset):
    "this is a class for tracking cryptocurrency information"
    def __init__(self, name, account=None):
        self.name = name
        self.balance = ''
        self.account = account
        self.symbol = getCryptoSymbolByName(self)
        self.price = getPriceInGnucash(self.symbol)
        self.gnuAccount = getAccountPath(self)
        self.gnuBalance = getGnuCashBalance(openGnuCashBook('Finance', True, True), self.gnuAccount)
                
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
        self.price = price
        
    def getSymbol(self):
        return self.symbol
    
    def updateSpreadsheetAndGnuCash(self):
        account = self.symbol if self.account == None else self.account
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
        updatePriceInGnucash(self.symbol, format(self.price, ".2f"))

    def updateMRBalance(self, myBook):
        today = datetime.today().date()
        transactions = [tr for tr in myBook.transactions
            if tr.post_date.year == today.year
            for spl in tr.splits
            if spl.account.fullname == self.gnuAccount]
        myBook.delete(transactions[0])
        with myBook as book:
            split = [Split(value=-Decimal(self.price), memo="scripted", account=myBook.accounts(fullname='Income:Market Research')),
                    Split(value=Decimal(self.price), quantity=Decimal(self.balance), memo="scripted", account=myBook.accounts(fullname=self.gnuAccount))]
            Transaction(post_date=today, currency=myBook.currencies(mnemonic="USD"), description=self.name + ' account balance', splits=split)
            book.save()
            book.flush()
            self.updateGnuBalance(book)
            book.close()

class USD(Asset):
    "this is a class for tracking USD information"
    def __init__(self, name):
        self.name = name
        self.balance = ""
        self.currency = 'USD'
        self.reviewTransactions = []
        self.account = None
        self.gnuAccount = getAccountPath(self)
        book = 'Home' if (self.name in ['Ally', 'BoA-joint', 'Home']) else 'Finance'
        balance = getGnuCashBalance(openGnuCashBook(book, True, True), self.gnuAccount)
        self.gnuBalance = round(balance, 2) if float(balance)>0 else 0
    
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
            openSpreadsheet(driver, 'Home', '2023 Balance')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC')
            updateSpreadsheet('Home', str(year) + ' Balance', self.name, month, balance, 'BoA CC', True)
        else:
            openSpreadsheet(driver, 'Checking Balance', '2023')
            updateSpreadsheet('Checking Balance', year, self.name, month, balance, self.name + " CC")
            updateSpreadsheet('Checking Balance', year, self.name, month, balance, self.name + " CC", True)
    
    def overwriteBalance(self, myBook):
        today = datetime.today().date()
        transactions = [tr for tr in myBook.transactions
            if tr.post_date.year == today.year
            for spl in tr.splits
            if spl.account.fullname == self.gnuAccount]
        myBook.delete(transactions[0])
        with myBook as book:
            split = [Split(value=-Decimal(self.balance), memo="scripted", account=myBook.accounts(fullname='Income:Market Research')),
                    Split(value=Decimal(self.balance), memo="scripted", account=myBook.accounts(fullname=self.gnuAccount))]
            Transaction(post_date=today, currency=myBook.currencies(mnemonic="USD"), description=self.name + ' account balance', splits=split)
            book.save()
            book.flush()
            self.updateGnuBalance(book)
            book.close()
            