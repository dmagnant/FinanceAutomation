from datetime import datetime;  from decimal import Decimal

if __name__ == "Classes.Asset":
    from Classes.Spreadsheet import Spreadsheet
    from Functions.GeneralFunctions import getCryptocurrencyPrice, getStartAndEndOfDateRange
    # from Functions.SpreadsheetFunctions import updateSpreadsheet
else:
    from scripts.scripts.Classes.Spreadsheet import Spreadsheet
    from scripts.scripts.Functions.GeneralFunctions import getCryptocurrencyPrice, getStartAndEndOfDateRange
    # from scripts.scripts.Functions.SpreadsheetFunctions import updateSpreadsheet

def getSymbolByName(self):
    match self.name.lower():
        case "bitcoin":                                             return 'BTC'
        case "cardano":                                             return 'ADA'
        case "ethereum":                                            return 'ETH'
        case 'he investment':                                       return "VIIIX"        
        case 'vfiax':                                               return "VFIAX"
        case 'vbirx':                                               return "VBIRX"
        case 'viiix':                                               return 'VIIIX'
        case "iotex":                                               return 'IOTX'
        case "presearch":                                           return 'PRE'
        case "bing":                                                return 'BNG'
        case "pinecone":                                            return 'PNCN'
        case "tellwut":                                             return 'TWT'
        case "swagbucks":                                           return 'SB'
        case 'small cap index':                                     return 'VSCIX'
        case 'employee benefit index':                              return 'M038'
        case 'extended market index':                               return 'M036'
        case 'total stock market':                                  return '8585'
        case 'fidelityiragme' | 'fidelityrothiragme' | 'fidelitybrokeragegme':          return 'GME'
        case 'fidelityiravti' | 'fidelityrothiravti' | 'fidelitybrokeragevti':          return 'VTI'
        case 'fidelityiravxus' | 'fidelityrothiravxus':                                 return 'VXUS'        
        case 'fidelityiraspaxx' | 'fidelityrothiraspaxx' | 'fidelitybrokeragespaxx':    return 'SPAXX'
        case _:                                                     print(f'Security: {self.name} not found in "getSymbolByName" function')

def updateCoinQuantityFromStakingInGnuCash(self, book):
    coinDifference = round(Decimal(self.balance) - Decimal(self.gnuBalance),3)
    amount = round(self.price * coinDifference, 3)
    if coinDifference > 0.001:
            splits = [book.createSplit(-amount, 'Income:Investments:Staking'), book.createSplit(amount, self.gnuAccount, quantity=coinDifference)]
            book.writeTransaction(datetime.today().date(), self.symbol + ' staking', splits)
    elif coinDifference < 0:
        print(f'given balance of {self.balance} {self.symbol} '
        f'minus gnuCash balance of {self.gnuBalance} '
        f'leaves unexpected coin difference of {coinDifference} '
        f'is it rounding issue?')                

class Asset:
    "this is a class for tracking asset information"
    def getName(self):              return self.name
    def getBalance(self):           return self.balance
    def setBalance(self, balance):  self.balance = balance
    # def getGnuAccount(self):        return self.getGnuAccountFullName(self.name)
    def getGnuBalance(self):        return self.gnuBalance
    def setValue(self, value):      self.value = value
    def setCost(self, cost):        self.cost = cost
    
class Security(Asset):    # this is a class for tracking security information
    def __init__(self, name, book, account=None):
        self.name = name
        self.balance = self.value = self.cost = ''
        self.symbol = getSymbolByName(self)
        self.price = book.getPriceInGnucash(self.symbol, datetime.today().date())
        self.gnuAccount = book.getGnuAccountFullName(name, account)
        self.gnuBalance = Decimal(book.getGnuAccountBalance(self.gnuAccount))
        self.gnuValue = self.getGnuValue()
    def getPrice(self):                     return self.price
    def getPriceFromCoinGecko(self):        return getCryptocurrencyPrice(self.name)[self.name.lower()]['usd']
    def setPrice(self, price):              self.price = Decimal(price)
    def getSymbol(self):                    return self.symbol      
    def updateGnuBalance(self, balance):
        hasattr(self, 'symbol')
        if hasattr(self, 'symbol'):
            self.gnuValue = self.getGnuValue()
        print(f'updating gnuBalance for {self.name} from {self.gnuBalance} to {balance}')
        self.gnuBalance = Decimal(balance)
    
    def getGnuValue(self):  price = Decimal(self.price);    return round(self.gnuBalance * price, 2) if float(self.gnuBalance * price)>0 else 0
    
    def updateGnuBalanceAndValue(self, balance):    
        self.gnuBalance = Decimal(balance); self.gnuValue = self.getGnuValue()
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'symbol: {self.symbol} \n'
                f'balance: {self.balance} \n'
                f'gnuBalance: {self.gnuBalance} \n'
                f'cost: {self.cost} \n'
                f'price: {self.price}')
        
    
    def updateSpreadsheetAndGnuCash(self, spreadsheet, book):
        spreadsheet.updateSpreadsheet(self.symbol, 1, self.balance, self.symbol)
        spreadsheet.updateSpreadsheet(self.symbol, 2, float(self.price), self.symbol)
        updateCoinQuantityFromStakingInGnuCash(self, book)
        self.updateGnuBalance(book.getGnuAccountBalance(self.gnuAccount))

    # def updateBalanceInSpreadSheet(self):
    #     updateSpreadsheet('Finances', 'Investments', self.symbol, 1, self.balance, self.symbol)

    # def updatePriceInSpreadSheet(self):
    #     updateSpreadsheet('Finances', 'Investments', self.symbol, 2, self.price, self.symbol)

    # def updateBalanceInGnuCash(self, book):
    #     updateCoinQuantityFromStakingInGnuCash(self, book)

class USD(Asset):
    "this is a class for tracking USD information"
    def __init__(self, name, book):
        self.balance = self.value = self.cost = ''
        self.name, self.units, self.currency, self.reviewTransactions = name, 0, 'USD', []
        # self.account = None
        self.gnuAccount = book.getGnuAccountFullName(name)
        self.gnuCashAccount = book.getGnuAccountByFullName(self.gnuAccount)
        balance = book.getGnuAccountBalance(self.gnuAccount)
        self.gnuBalance = round(balance, 2) if float(balance)>0 else 0
    def getReviewTransactions(self):                return self.reviewTransactions
    def setReviewTransactions(self, transactions):  self.reviewTransactions.append(transactions)
    def updateGnuBalance(self, balance):            
        print(f'updating gnuBalance for {self.name} from {self.gnuBalance} to {balance}')
        self.gnuBalance = round(Decimal(balance), 2)
    
    def getData(self):
        print(  f'name: {self.name} \n'
                f'   balance: ${self.balance} \n'
                f'gnuBalance: ${self.gnuBalance}')
        if self.reviewTransactions: print(f'Review Transactions: \n 'f'{self.reviewTransactions}')
        
    def locateAndUpdateSpreadsheet(self, driver):
        balance = 0.00 if float(self.balance) < 0 else float(self.balance) * -1
        if self.value: balance = self.value
        today = datetime.today()
        month, year = today.month, today.year
        # switch worksheets if running in December (to next year's worksheet)
        if month == 12: year = year + 1
        if self.name == 'BoA-joint':
            Home = Spreadsheet('Home', str(year) + ' Balance', driver)
            Home.updateSpreadsheet(self.name, month, balance, modifiedCC=True)
        else:
            CheckingBalance = Spreadsheet('Finances', str(year))
            column = CheckingBalance.projectedColumns[month-1]
            row = CheckingBalance.projectedRows[month-1]
            while True:
                description = CheckingBalance.readCell(column+str(row))
                if description and self.name in description:
                    break
                else:   row+=1
            CheckingBalance.writeCell(chr(ord(column) + 1) + str(row), balance)
            CheckingBalance.writeCell(chr(ord(column) + 4) + str(row), balance)
    
    def getInterestTotalForDateRange(self, book):
        interestAccount = book.getGnuAccountFullName('Interest')
        dateRange = getStartAndEndOfDateRange(timeSpan='all', minDate=datetime(2022,1,1,0,0,0).date())
        allInvestmentTransactions = book.getTransactionsByGnuAccountAndDateRange(self.gnuAccount, dateRange)
        savingsTransactions = book.getTransactionsByGnuAccount(self.gnuAccount, transactionsToFilter=allInvestmentTransactions)
        totalInterest = 0
        for tr in savingsTransactions:
            for spl in tr.splits:
                if spl.account.fullname == interestAccount:
                    totalInterest += abs(spl.value)
        print('total interest for: ' + self.name + ' is: ' + str(totalInterest))
        return round(Decimal(totalInterest),2)
