import csv
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from os import listdir

import piecash
from piecash import GnucashException, Price, Split, Transaction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == "Classes.GnuCash":
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername,
                                            modifyTransactionDescription,
                                            setDirectory, showMessage)
else:
    from scripts.scripts.Functions.GeneralFunctions import (getPassword, getStartAndEndOfDateRange, getUsername,
        modifyTransactionDescription, setDirectory, showMessage)

def openGnuCashBook(type, readOnly):
    if type == 'Finance':
        bookPathSuffix = r"\Finances\Personal Finances\Finance.gnucash"
    elif type == 'Home':
        bookPathSuffix = r"\Stuff\Home\Finances\Home.gnucash"
    elif type == 'Test':
        bookPathSuffix = r"\Finances\Personal Finances\test.gnucash"
    book = setDirectory() + bookPathSuffix
    try:
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=readOnly, check_same_thread=False)
    except GnucashException:
        showMessage("Gnucash file open", "Close Gnucash file then click OK")
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=readOnly, check_same_thread=False)
    return myBook

class GnuCash:
    "this is a class for holding gnucash book objects"
    def __init__(self, type):
        self.type = type
        self.readBook = openGnuCashBook(self.type, True)
        self.writeBook = False
    
    def getWriteBook(self): 
        if not self.writeBook:
            self.writeBook = openGnuCashBook(self.type, False)
        return self.writeBook
    
    def closeBook(self):
        self.readBook.close()
        if self.writeBook:
            if not self.writeBook.is_saved:
                self.writeBook.save()
            self.writeBook.close()
    
    def getBalance(self, accountPath):
        book = self.getWriteBook() if (self.writeBook and not self.writeBook.is_saved) else self.readBook
        balance = book.accounts(fullname=accountPath).get_balance(at_date=datetime.today().date())
        return str(balance).replace('-', '') if balance == 0 else balance
    
    # def getTransactions(self):
    #     if self.getWriteBook() and not self.writeBook.is_saved:
    #         transactions = self.writeBook.transactions
    #     else:
    #         transactions = self.readBook.transactions
    #     return transactions
    
    def updateMRBalance(self, account):
        book = self.getWriteBook()
        today = datetime.today().date()
        transactions = [tr for tr in book.transactions
            if tr.post_date.year == today.year
            for spl in tr.splits
            if spl.account.fullname == account.gnuAccount]
        value = int(account.balance) * account.price
        try:
            book.delete(transactions[0])
        except IndexError:
            exception = 'no prior years transactions to delete'
        split = [Split(value=-value, memo="scripted", account=book.accounts(fullname='Income:Market Research')),
                Split(value=value, quantity=Decimal(account.balance), memo="scripted", account=book.accounts(fullname=account.gnuAccount))]
        Transaction(post_date=today, currency=book.currencies(mnemonic="USD"), description=account.name + ' account balance', splits=split)
        book.flush()
        account.updateGnuBalance(self.getBalance(account.gnuAccount))
        
    def overwriteBalance(self, account):
        today = datetime.today().date()
        myBook = self.getWriteBook()
        transactions = [tr for tr in myBook.transactions
            if tr.post_date.year == today.year
            for spl in tr.splits
            if spl.account.fullname == account.gnuAccount]
        myBook.delete(transactions[0])
        split = [Split(value=-Decimal(account.balance), memo="scripted", account=myBook.accounts(fullname='Income:Market Research')),
                Split(value=Decimal(account.balance), memo="scripted", account=myBook.accounts(fullname=account.gnuAccount))]
        Transaction(post_date=today, currency=myBook.currencies(mnemonic="USD"), description=account.name + ' account balance', splits=split)
        myBook.flush()
        account.updateGnuBalance(self.getBalance(account.gnuAccount))

    
    def purgeOldGnucashFiles(self):
        dateRange = getStartAndEndOfDateRange(datetime.today().date(), 14)
        suffix = r'\Finances\Personal Finances' if self.type == 'Finance' else r'\Stuff\Home\Finances'
        directory = setDirectory() + suffix
        for fileName in listdir(directory):
            filePath = (directory + r'\'' + fileName).replace("'",'')
            fileModifiedDate = datetime.fromtimestamp(os.path.getmtime(filePath)).date()
            if fileModifiedDate < dateRange['startDate']:
                os.remove(filePath)
    
    def openGnuCashUI(self):
        path = r"\Finances\Personal Finances\Finance.gnucash" if self.type == 'Finance' else r"\Stuff\Home\Finances\Home.gnucash"
        os.startfile(setDirectory() + path)
    
    def getPriceInGnucash(self, symbol, date=''):
        myBook = self.getWriteBook() if (self.writeBook and not self.writeBook.is_saved) else self.readBook
        if date:
            price = ''
            while not price:
                try:
                    price =  myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=date).value
                    if price == 0:
                        print('price for ' + symbol + ' is 0, remove from price database to prevent loop')
                except KeyError:
                    date = date - timedelta(days=1)
            return price
        else:
            return myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD")).value 
        
    def updatePriceInGnucash(self, symbol, price):
        myBook = self.getWriteBook()
        try:
            gnuCashPrice = myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=datetime.today().date())  # raise a KeyError if Price does not exist
            if str(gnuCashPrice.value) == price:
                return
            gnuCashPrice.value = Decimal(price)
        except KeyError:
            Price(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=datetime.today().date(), value=Decimal(price), source="user:price", type="last")
        myBook.flush()
        
        
    def writeSimpleTransaction(self, transactionInfo):
        myBook = self.getWriteBook()
        split=[Split(value=transactionInfo['amount'], account=myBook.accounts(fullname=transactionInfo['toAccount'])),
            Split(value=-transactionInfo['amount'], account=myBook.accounts(fullname=transactionInfo['fromAccount']))]
        Transaction(post_date=transactionInfo['date'], currency=myBook.currencies(mnemonic="USD"), description=transactionInfo['description'], splits=split)
        myBook.flush()
        
    def writeStakingTransaction(self, transactionInfo):
        myBook = self.getWriteBook()
        split = [Split(value=-transactionInfo['amount'], memo="scripted", account=myBook.accounts(fullname='Income:Investments:Staking')),
                Split(value=transactionInfo['amount'], quantity=transactionInfo['coinDifference'], memo="scripted", account=myBook.accounts(fullname=transactionInfo['toAccount']))]
        Transaction(post_date=datetime.today().date(), currency=myBook.currencies(mnemonic="USD"), description=transactionInfo['description'], splits=split)
        myBook.flush()        
                   
    def writeCryptoTransaction(self):
        myBook = self.getWriteBook()
        from_account = 'Assets:Liquid Assets:Sofi:Checking'
        to_account = 'Assets:Non-Liquid Assets:CryptoCurrency:Cardano'
        fee_account = 'Expenses:Bank Fees'
        amount = Decimal(50.00)
        description = 'ADA purchase'
        today = datetime.today()
        year = today.year
        postdate = today.replace(month=1, day=1, year=year)
        split = [Split(value=-amount, memo="scripted", account=myBook.accounts(fullname=from_account)),
                Split(value=round(amount-Decimal(1.99), 2), quantity=round(Decimal(35.052832), 6), memo="scripted", account=myBook.accounts(fullname=to_account)),
                Split(value=round(Decimal(1.99),2), memo="scripted", account=myBook.accounts(fullname=fee_account))]
        Transaction(post_date=postdate.date(), currency=myBook.currencies(mnemonic="USD"), description=description, splits=split)
        myBook.flush()
        
    def writeUtilityTransaction(self, transactionInfo):
        myBook = self.getWriteBook()
        split=[Split(value=transactionInfo['electricity'], account=myBook.accounts(fullname="Expenses:Utilities:Electricity")),
            Split(value=transactionInfo['gas'], account=myBook.accounts(fullname="Expenses:Utilities:Gas")),
            Split(value=-round(Decimal(transactionInfo['total']), 2), account=myBook.accounts(fullname="Assets:Ally Checking Account"))]
        Transaction(post_date=datetime.today().date().replace(day=24), currency=myBook.currencies(mnemonic="USD"), description='WE ENERGIES PAYMENT', splits=split)
        myBook.flush()
        
    def getTotalOfAutomatedMRAccounts(self):
        myBook = self.readBook
        mrTotal = 0
        swagbucks = 0
        tellwut = 0
        bing = 0
        sago = 0
        pinecone = 0
        paidviewpoint = 0
        knowledgePanel = 0
        paypal = 0
        appen = 0
        reckner = 0
        check = 0
        promo = 0
        antidote = 0
        amazonGC = 0
        ccRewards = 0
        accelerant = 0
        kitchenInsiders = 0
        onlineInsights = 0
        for transaction in myBook.transactions:
            if transaction.post_date.year == 2023:
                for spl in transaction.splits:
                    if 'Income:Market Research' in spl.account.fullname:
                        mrTotal += -spl.value
                        if 'swagbucks' in transaction.description.lower():
                            swagbucks += -spl.value
                        elif 'tellwut' in transaction.description.lower():
                            tellwut += -spl.value
                        elif 'bing' in transaction.description.lower():
                            bing += -spl.value
                        elif 'sago' in transaction.description.lower():
                            sago += -spl.value
                        elif 'pinecone' in transaction.description.lower():
                            pinecone += -spl.value
                        elif 'paidviewpoint' in transaction.description.lower():
                            paidviewpoint += -spl.value
                        elif 'knowledgepanel' in transaction.description.lower():
                            knowledgePanel += -spl.value
                        elif 'paypal' in transaction.description.lower():
                            paypal += -spl.value
                        elif 'reckner' in transaction.description.lower():
                            reckner += -spl.value
                        elif 'mobile check deposit' in transaction.description.lower():
                            check += -spl.value
                        elif 'bank promo' in transaction.description.lower():
                            promo += -spl.value
                        elif 'antidote' in transaction.description.lower():
                            antidote += -spl.value
                        elif 'appen' in transaction.description.lower() or 'mystery shopping' in transaction.description.lower():
                            appen += -spl.value
                        elif 'cc rewards' in transaction.description.lower():
                            ccRewards+= -spl.value
                        elif 'accelerant' in transaction.description.lower():
                            accelerant+= -spl.value
                        elif 'kitchen insider' in transaction.description.lower():
                            kitchenInsiders+= -spl.value
                        elif 'online insights' in transaction.description.lower():
                            onlineInsights+= -spl.value                            
                        else:
                            print(transaction.description)
                    if spl.account.fullname == 'Assets:Liquid Assets:Amazon GC':
                        if spl.value > 0:
                            amazonGC += spl.value
                            
        accountedTotal = swagbucks + tellwut + bing + sago + pinecone + paidviewpoint + knowledgePanel + paypal + appen + reckner + check + promo + antidote + ccRewards + accelerant + kitchenInsiders + onlineInsights

        print('           promo: ' + str(promo))
        print('           appen: ' + str(appen))
        print('         reckner: ' + str(reckner))
        print('       swagbucks: ' + str(swagbucks))
        print('            sago: ' + str(sago))        
        print('  knowledgePanel: ' + str(knowledgePanel))        
        print('   paidviewpoint: ' + str(paidviewpoint))
        print('        ccRewards: ' + str(ccRewards))             
        print('         tellwut: ' + str(tellwut))        
        print('        pinecone: ' + str(pinecone))
        print('        onlineInsights: ' + str(onlineInsights))        
        print('        antidote: ' + str(antidote))
        print('           misc.: ' + str(mrTotal - accountedTotal))        
        print('        kitchenInsiders: ' + str(kitchenInsiders))
        print('        accelerant: ' + str(accelerant))
        print('            bing: ' + str(bing))        
        print('           check: ' + str(check))
        print('          paypal: ' + str(paypal))    
        print('        MR total: ' + str(mrTotal))
        print('paid in amazonGC: ' + str(amazonGC))
        
    def consolidatePastYearsTransactions(self):
        myBook = self.getWriteBook()
        today = datetime.today().date()
        transDate = today.replace(month=12, day=31)
        year = 2022
        while year < today.year:
            transDate = transDate.replace(year=year)
            transactions = []
            accounts = []
            totalValues = []
            totalQuantities = []
            splits = []
            for transaction in myBook.transactions:
                if transaction.post_date.year == transDate.year:
                    transactions.append(transaction)
                    for spl in transaction.splits:
                        splitAccount = spl.account.fullname
                        if splitAccount not in accounts:
                            accounts.append(splitAccount)
                            totalValues.append(0)
                            totalQuantities.append(0)
                        i = accounts.index(splitAccount)
                        totalValues[i] += spl.value
                        if "Staking" in splitAccount or "CryptoCurrency" in splitAccount:
                            totalQuantities[i] += spl.quantity
                    myBook.delete(transaction)
            for account in accounts:
                i = accounts.index(account)
                if "Staking" in account or "CryptoCurrency" in account:
                    splits.append(Split(value=totalValues[i], quantity=totalQuantities[i], memo="", account=myBook.accounts(fullname=account)))
                else:
                    splits.append(Split(value=totalValues[i], memo="", account=myBook.accounts(fullname=account)))
            Transaction(post_date=transDate, currency=myBook.currencies(mnemonic="USD"), description=str(transDate.year) + ' Totals', splits=splits)
            year += 1
            
        for transaction in myBook.transactions:
            for spl in transaction.splits:
                if spl.value == 0 and spl.quantity == 0:
                    myBook.delete(spl)
        myBook.flush()

    def getDollarsInvestedPerSecurity(self, security):
        # get dollars invested balance (must be run per security)
        mybook = self.readBook
        total = 0
        # retrieve transactions from GnuCash
        transactions = [tr for tr in mybook.transactions
                        for spl in tr.splits
                        if spl.account.fullname == security.gnuAccount]
        for tr in transactions:
            amount = 0
            stakingTrans = False
            for spl in tr.splits:
                if spl.account.fullname == security.gnuAccount:
                    amount = format(spl.value, ".2f")
                elif spl.account.fullname == "Income:Investments:Staking":
                    stakingTrans = True
            if not stakingTrans:
                total += abs(float(amount))
        print(f'total $ invested in {security.name}: ' + str(total))
        return total
    
    def importUniqueTransactionsToGnuCash(self, account, transactionsCSV, driver, dateRange, lineStart=1):
        directory = setDirectory()
        importCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\import.csv"
        open(importCSV, 'w', newline='').truncate()
        if account.name == 'Ally':
            gnuAccount = "Assets:Ally Checking Account"
            gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_ally.csv"
        elif account.name == 'Sofi Checking':
            gnuAccount = "Assets:Liquid Assets:Sofi:Checking"
            gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_sofi.csv"
        elif account.name == 'Sofi Savings':
            gnuAccount = "Assets:Liquid Assets:Sofi:Savings"
            gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_sofi.csv"
        open(gnuCSV, 'w', newline='').truncate()
        transactions = [tr for tr in self.readBook.transactions
                        if tr.post_date >= dateRange['startDate'] and tr.post_date <= dateRange['endDate']
                        for spl in tr.splits
                        if spl.account.fullname == gnuAccount]
        for tr in transactions:
            date = str(tr.post_date.strftime('%Y-%m-%d'))
            description = str(tr.description)
            for spl in tr.splits:
                amount = format(spl.value, ".2f")
                if spl.account.fullname == gnuAccount:
                    transactionRow = date, description, str(amount)
                    csv.writer(open(gnuCSV, 'a', newline='')).writerow(transactionRow)
        for row in csv.reader(open(transactionsCSV, 'r'), delimiter=','):
            if row not in csv.reader(open(gnuCSV, 'r'), delimiter=','):
                csv.writer(open(importCSV, 'a', newline='')).writerow(row)
        self.importGnuTransaction(account, importCSV, driver, lineStart)
        
    def importGnuTransaction(self, account, transactionsCSV, driver, lineStart=1):
        def setToAccount(account, description):
            toAccount = ''
            if "BoA CC" in description:
                if "Rewards" in description:
                    toAccount = "Income:Market Research:Credit Card Rewards"  
                else: 
                    if account == 'Ally':
                        toAccount = "Liabilities:BoA Credit Card"
                    elif "Sofi" in account:
                        toAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"
            elif "Interest Earned" in description:
                toAccount = "Income:Investments:Interest"
            elif 'HSA Investment' in description:
                toAccount = 'Assets:Non-Liquid Assets:HSA:NM HSA Cash'
            elif 'IRA Contribution' in description or 'IRA sale of stock' in description:
                toAccount = 'Assets:Non-Liquid Assets:IRA:Fidelity'
            elif 'IRA Investment' in description:
                toAccount = 'Assets:Non-Liquid Assets:IRA:Fidelity:Govt Money Market'
            elif 'HSA Dividend' in description or '401k Dividend' in description or 'IRA Dividend' in description:
                toAccount = 'Income:Investments:Dividends'
            elif '401k Investment' in description:
                toAccount = 'Assets:Non-Liquid Assets:401k'
            elif "Investment Admin Fee " in description or '401k Fee' in description:
                toAccount = "Expenses:Bank Fees"
            elif "Savings Transfer" in description:
                toAccount = "Assets:Liquid Assets:Sofi:Savings"        
            elif "Tessa Deposit" in description:
                toAccount = "Tessa's Contributions"
            elif "Jonny payment" in description:
                toAccount = "Liabilities:Loans:Personal Loan"
            elif "MyConstant transfer" in description:
                toAccount = "Assets:Liquid Assets:My Constant"
            elif "Water Bill" in description:
                toAccount = "Expenses:Utilities:Water"
            elif "Dan Deposit" in description:
                toAccount = "Dan's Contributions"
            elif "Mortgage Payment" in description:
                toAccount = "Liabilities:Mortgage Loan"
            elif "Swagbucks" in description:
                toAccount = "Income:Market Research:Swagbucks"
            elif "NM Paycheck" in description or "SF Paycheck" in description:
                toAccount = "Income:Salary"
            elif "GOOGLE FI" in description.upper() or "GOOGLE *FI" in description.upper():
                toAccount = "Expenses:Utilities:Phone"
            elif "Alliant Transfer" in description:
                toAccount = "Assets:Liquid Assets:Promos:Alliant"
            elif 'HSA Employer Contribution' in description:
                toAccount = "Income:Employer Contributions:HSA Contributions"
            elif "KAINTH" in description:
                toAccount = "Expenses:Groceries"
            elif "MINI MARKET MILWAUKEE WI" in description:
                toAccount = "Expenses:Groceries"
            elif "CRYPTO PURCHASE" in description.upper():
                toAccount = "Assets:Non-Liquid Assets:CryptoCurrency"
            elif "Pinecone" in description:
                toAccount = "Income:Market Research:Pinecone"
            elif "Internet Bill" in description:
                toAccount = "Expenses:Utilities:Internet"
            elif "TRAVEL CREDIT" in description:
                toAccount = "Income:Credit Card Rewards"
            elif "MILWAUKEE ELECTRIC TO" in description:
                toAccount = "Expenses:Home Expenses:Maintenance"
            elif "CASH REWARDS STATEMENT CREDIT" in description:
                toAccount = "Income:Market Research:Credit Card Rewards"        
            elif "Chase CC Rewards" in description:
                toAccount = "Income:Market Research:Credit Card Rewards"
            elif "Chase CC" in description:
                toAccount = "Liabilities:Credit Cards:Chase Freedom"
            elif "Discover CC Rewards" in description:
                toAccount = "Income:Market Research:Credit Card Rewards"        
            elif "Discover CC" in description:
                toAccount = "Liabilities:Credit Cards:Discover It"
            elif "Amex CC Rewards" in description:
                toAccount = "Income:Market Research:Credit Card Rewards"
            elif "Amex CC" in description:
                toAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
            elif "Barclays CC Rewards" in description:
                toAccount = "Income:Market Research:Credit Card Rewards"
            elif "Barclays CC" in description:
                toAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
            elif "Ally Transfer" in description:
                toAccount = "Expenses:Joint Expenses"    
            elif "BP#" in description:
                toAccount = "Expenses:Transportation:Gas (Vehicle)"
            elif "CAT DOCTOR" in description:
                toAccount = "Expenses:Medical:Vet"
            elif "APPEN" in description:
                toAccount = "Income:Market Research:Appen"
            elif "PARKING" in description or "SPOTHERO" in description.upper():
                toAccount = "Expenses:Transportation:Parking"
            elif "PROGRESSIVE" in description:
                toAccount = "Expenses:Transportation:Car Insurance"
            elif "CHARTER SERVICES" in description.upper():
                toAccount = "Expenses:Utilities:Internet"     
            elif "UBER" in description.upper() and "EATS" in description.upper():
                toAccount = "Expenses:Bars & Restaurants"
            elif "UBER" in description.upper():
                toAccount = "Expenses:Travel:Ride Services" if account in ['BoA-joint', 'Ally'] else "Expenses:Transportation:Ride Services"
            elif "TECH WAY AUTO SERV" in description.upper():
                toAccount = "Expenses:Transportation:Car Maintenance"
            elif "INTEREST PAID" in description.upper():
                toAccount = "Income:Interest" if account in ['BoA-joint', 'Ally'] else "Income:Investments:Interest"
            if not toAccount:
                for i in ['HOMEDEPOT.COM', 'HOME DEPOT']:
                    if i in description.upper():
                        if account in ['BoA-joint', 'Ally']:
                            toAccount = "Expenses:Home Depot"
            
            if not toAccount:
                for i in ['AMAZON', 'AMZN']:
                    if i in description.upper():
                        toAccount = "Expenses:Amazon"

            if not toAccount:
                if len(row) >= 5:
                    if row[3] == "Groceries" or row[4] == "Supermarkets":
                        toAccount = "Expenses:Groceries"
                if not toAccount:
                    for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET']:
                        if i in description.upper():
                            toAccount = "Expenses:Groceries"

            if not toAccount:
                if len(row) >= 5:
                    if row[3] == "Food & Drink" or row[4] == "Restaurants":
                        toAccount = "Expenses:Bars & Restaurants"
                if not toAccount:
                    for i in ['MCDONALD', 'GRUBHUB', 'JIMMY JOHN', 'COLECTIVO', 'INSOMNIA', 'EATSTREET', "KOPP'S CUSTARD", 'MAHARAJA', 'STARBUCKS', "PIETRO'S PIZZA", 'SPROCKET CAFE']:
                        if i in description.upper():
                            toAccount = "Expenses:Bars & Restaurants"
            
            if not toAccount:
                toAccount = "Expenses:Other"
            return toAccount
        def formatTransactionVariables(account, row):
            skipTransaction = False
            if account.name == 'Ally':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = row[1]
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
            elif account.name == 'Amex':
                postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
                description = row[1]
                amount = -Decimal(row[2])
                if "AUTOPAY PAYMENT" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
            elif account.name == 'Barclays':
                postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
                description = row[1]
                amount = Decimal(row[3])
                if "PAYMENT RECEIVED" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[3]
            elif account.name == 'BoA':
                postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
                description = row[2]
                amount = Decimal(row[4])
                if "BA ELECTRONIC PAYMENT" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[2] + ", " + row[4]
            elif account.name == 'BoA-joint':
                postDate = datetime.strptime(row[0], '%m/%d/%Y').date()
                description = row[2]
                amount = Decimal(row[4])
                if "BA ELECTRONIC PAYMENT" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[2] + ", " + row[4]
            elif account.name == 'Chase':
                postDate = datetime.strptime(row[1], '%m/%d/%Y').date()
                description = row[2]
                amount = Decimal(row[5])
                if "AUTOMATIC PAYMENT" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[1] + ", " + row[2] + ", " + row[5]
            elif account.name == 'Discover':
                postDate = datetime.strptime(row[1], '%m/%d/%Y').date()
                description = row[2]
                amount = -Decimal(row[3])
                if "DIRECTPAY FULL BALANCE" in description.upper():
                    skipTransaction = True
                fromAccount = account.gnuAccount
                reviewTransPath = row[1] + ", " + row[2] + ", " + row[3]
            elif account.name == 'Sofi Checking':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = row[1]
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
            elif account.name == 'Sofi Savings':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = row[1]
                if "CHECKING - 6915" in description.upper():
                    skipTransaction = True
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
            elif account.name == 'HSA Cash':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = row[1]
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]                
            elif account.name == 'HSA Investment': 
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = modifyTransactionDescription(row[1])
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                shares = float(row[3])
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
                return {'postDate': postDate, 'description': description, 'amount': amount, 'skipTransaction': skipTransaction, 'fromAccount': fromAccount, 'reviewTransPath': reviewTransPath, 'shares': shares}
            elif account.name == 'IRA':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                description = row[1]
                amount = Decimal(row[2])
                fromAccount = account.gnuAccount
                if "TOTAL INTERNATIONAL STOCK" in description and "DIVIDEND" not in description:
                    fromAccount += ":Total Intl Stock Market"
                elif "TOTAL STK MKT ETF" in description and "DIVIDEND" not in description:
                    fromAccount += ":Total Stock Market"
                elif "DIVIDEND" in description or 'YOU SOLD' in description:
                    fromAccount += ":Govt Money Market"
                description = modifyTransactionDescription(description)
                shares = float(row[3])
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
                return {'postDate': postDate, 'description': description, 'amount': amount, 'skipTransaction': skipTransaction, 'fromAccount': fromAccount, 'reviewTransPath': reviewTransPath, 'shares': shares}
            elif account.name == 'Vanguard401k':
                postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
                amount = Decimal(row[3])
                description = row[1]
                fromAccount = account.gnuAccount
                if "Instl Tot Stk Mkt" in description:
                    fromAccount += ":Total Stock Market"
                elif 'Employee Benefit Index' in description:
                    fromAccount += ":Employee Benefit Index"
                shares = float(row[2])
                description = modifyTransactionDescription(description)
                reviewTransPath = row[0] + ", " + row[1] + ", " + row[3]
                return {'postDate': postDate, 'description': description, 'amount': amount, 'skipTransaction': skipTransaction, 'fromAccount': fromAccount, 'reviewTransPath': reviewTransPath, 'shares': shares}
            description = modifyTransactionDescription(description)
            return {'postDate': postDate, 'description': description, 'amount': amount, 'skipTransaction': skipTransaction, 'fromAccount': fromAccount, 'reviewTransPath': reviewTransPath}
        def getEnergyBillAmounts(driver, amount, energyBillNum):
            if energyBillNum == 1:
                driver.openNewWindow('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx')
                time.sleep(2)
                try:
                    # driver.webDriver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername('WE-Energies (Home)'))
                    # driver.webDriver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword('WE-Energies (Home)'))
                    driver.webDriver.find_element(By.XPATH, "//*[@id='next']").click() # login
                    time.sleep(4)
                    driver.webDriver.find_element(By.XPATH, "//*[@id='notInterested']/a").click # close out of app notice
                except NoSuchElementException:
                    exception = "caught"
                driver.webDriver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click() # view bill history
                time.sleep(4)
            billRow = 2
            billColumn = 7
            billFound = "no"
            while billFound == "no": # find bill based on comparing amount from Arcadia (weBill)
                weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
                weBillAmount = driver.webDriver.find_element(By.XPATH, weBillPath).text.replace('$', '')
                if str(abs(amount)) == weBillAmount:
                    billFound = "yes"
                else:
                    billRow += 1
            billColumn -= 2
            weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
            gas = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
            billColumn -= 2
            weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
            electricity = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
            return {'electricity': electricity, 'gas': gas, 'total': amount}

        rowCount = 0
        lineCount = 0
        energyBillNum = 0
        for row in csv.reader(open(transactionsCSV), delimiter=','):
            rowCount += 1
            if lineCount < lineStart: # skip header line
                lineCount += 1
            else:
                transactionVariables = formatTransactionVariables(account, row)
                if transactionVariables['skipTransaction']:
                    continue
                else:
                    toAccount = setToAccount(account.name, transactionVariables['description'])
                    if 'WE ENERGIES' in transactionVariables['description'].upper():
                        energyBillNum += 1
                        transactionVariables['amount'] = getEnergyBillAmounts(driver, transactionVariables['amount'], energyBillNum)
                    elif 'PAYCHECK' in transactionVariables['description'].upper() or "CRYPTO PURCHASE" in transactionVariables['description'].upper() or toAccount == "Expenses:Other":
                        account.setReviewTransactions(transactionVariables['reviewTransPath'])
                    self.writeGnuTransaction(transactionVariables, toAccount)
        account.updateGnuBalance(self.getBalance(account.gnuAccount))
        
    def writeGnuTransaction(self, transactionVariables, toAccount=''):
        myBook = self.getWriteBook()
        if "Contribution + Interest" in transactionVariables['description']:
            split = [Split(value=transactionVariables['amount']['interest'], memo="scripted", account=myBook.accounts(fullname="Income:Investments:Interest")),
                    Split(value=transactionVariables['amount']['employerContribution'], memo="scripted",account=myBook.accounts(fullname="Income:Employer Contributions:Pension Contributions")),
                    Split(value=transactionVariables['amount']['accountChange'], memo="scripted",account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "HSA Investment" in transactionVariables['description'] or "HSA Dividend" in transactionVariables['description'] or '401k' in transactionVariables['description'] or 'IRA Contribution' in transactionVariables['description'] or 'IRA Dividend' in transactionVariables['description']:
            split = [Split(value=-transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=transactionVariables['amount'], quantity=round(Decimal(transactionVariables['shares']), 3), memo="scripted", account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "Fidelity IRA Transfer" in transactionVariables['description']:
            split = [Split(value=-transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=transactionVariables['amount'], quantity=round(Decimal(transactionVariables['amount']), 2), memo="scripted", account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif 'IRA Investment' in transactionVariables['description']:
            split = [Split(value=-transactionVariables['amount'], quantity=-round(Decimal(transactionVariables['amount']), 2), memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=transactionVariables['amount'], quantity=round(Decimal(transactionVariables['shares']), 3), memo="scripted", account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "WE ENERGIES" in transactionVariables['description'].upper():
            split=[Split(value=transactionVariables['amount']['electricity'], account=myBook.accounts(fullname="Expenses:Utilities:Electricity")),
                    Split(value=transactionVariables['amount']['gas'], account=myBook.accounts(fullname="Expenses:Utilities:Gas")),
                    Split(value=transactionVariables['amount']['total'], account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "NM Paycheck" in transactionVariables['description']:
            split = [Split(value=round(Decimal(2032.62), 2), memo="scripted",account=myBook.accounts(fullname=transactionVariables['fromAccount'])),
                    Split(value=round(Decimal(693.60), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:401k")),
                    Split(value=round(Decimal(5.49), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Dental")),
                    Split(value=round(Decimal(44.90), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Health")),
                    Split(value=round(Decimal(2.93), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Vision")),
                    Split(value=round(Decimal(226.51), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Social Security")),
                    Split(value=round(Decimal(52.97), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Medicare")),
                    Split(value=round(Decimal(462.59), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Federal Tax")),
                    Split(value=round(Decimal(179.64), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:State Tax")),
                    Split(value=round(Decimal(152.08), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:HSA:NM HSA Cash")),
                    Split(value=-round(Decimal(3853.33), 2), memo="scripted",account=myBook.accounts(fullname=toAccount))]
        elif "SF Paycheck" in transactionVariables['description']:
            split = [Split(value=round(Decimal(2029.77), 2), memo="scripted",account=myBook.accounts(fullname=transactionVariables['fromAccount'])),
                    Split(value=round(Decimal(475.00), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:401k")),
                    Split(value=round(Decimal(8.81), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Dental")),
                    Split(value=round(Decimal(37.50), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Health")),
                    Split(value=round(Decimal(5.73), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Vision")),
                    Split(value=round(Decimal(226.54), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Social Security")),
                    Split(value=round(Decimal(58.98), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Medicare")),
                    Split(value=round(Decimal(490.04), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Federal Tax")),
                    Split(value=round(Decimal(181.83), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:State Tax")),
                    Split(value=round(Decimal(163.23), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:HSA:SF HSA")),
                    Split(value=-round(Decimal(25.00), 2), memo="scripted",account=myBook.accounts(fullname="Income:Employer Contributions:HSA Contributions")),                    
                    Split(value=-round(Decimal(3653.85), 2), memo="scripted",account=myBook.accounts(fullname=toAccount))]            
        else:
            split = [Split(value=-transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        Transaction(post_date=transactionVariables['postDate'], currency=myBook.currencies(mnemonic="USD"), description=transactionVariables['description'], splits=split)
        myBook.flush()