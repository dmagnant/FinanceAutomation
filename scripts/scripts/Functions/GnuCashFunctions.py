import csv
import os
from datetime import datetime
from decimal import Decimal
from os import listdir

import piecash
from piecash import GnucashException, Price, Split, Transaction

from .GeneralFunctions import (getStartAndEndOfDateRange, setDirectory,
                               showMessage)
from .TransactionFunctions import (formatTransactionVariables,
                                   getEnergyBillAmounts,
                                   modifyTransactionDescription, setToAccount)

def openGnuCashBook(type, readOnly, openIfLocked):
    directory=setDirectory()
    if type == 'Finance':
        book = directory + r"\Finances\Personal Finances\Finance.gnucash"
    elif type == 'Home':
        book = directory + r"\Stuff\Home\Finances\Home.gnucash"
    elif type == 'Test':
        book = directory + r"\Finances\Personal Finances\test.gnucash"
    try:
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    except GnucashException:
        showMessage("Gnucash file open", f'Close Gnucash file then click OK \n')
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    return myBook

def getGnuCashBalance(myBook, accountPath):
    with myBook as book:
        balance = book.accounts(fullname=accountPath).get_balance()
    book.close()
    return balance

def getAccountPath(accountName):
    match accountName:
        case 'Cardano':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano"            
        case 'Algorand':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Algorand"
        case 'Ally':
            return "Assets:Ally Checking Account"
        case 'AmazonGC':
            return "Assets:Liquid Assets:Amazon GC"
        case 'Amex':
            return "Liabilities:Credit Cards:Amex BlueCash Everyday"
        case 'Cosmos':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cosmos"                  
        case 'Barclays':
            return "Liabilities:Credit Cards:BarclayCard CashForward"
        case 'Bitcoin':
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
        case 'Polkadot':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Polkadot"
        case 'Ethereum':
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
        case 'IoTex':
            return "Assets:Non-Liquid Assets:CryptoCurrency:IoTex"
        case 'Liquid Assets':
            return "Assets:Liquid Assets"
        case 'Loopring':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Loopring"              
        case 'MyConstant':
            return "Assets:Liquid Assets:Bonds:My Constant"
        case 'Presearch':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Presearch"
        case 'Checking':
            return "Assets:Liquid Assets:Sofi:Checking"
        case 'Savings':
            return "Assets:Liquid Assets:Sofi:Savings"                
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Bonds:Worthy Bonds"
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')
            
def importGnuTransaction(account, transactionsCSV, driver, lineStart=1):
    book = 'Home' if (account.name == 'Ally' or account.name == 'BoA-joint') else 'Finance'
    myBook = openGnuCashBook(book, False, False)
    reviewTrans = ''
    rowCount = 0
    lineCount = 0
    energyBillNum = 0
    for row in csv.reader(open(transactionsCSV), delimiter=','):
        rowCount += 1
        # skip header line
        if lineCount < lineStart:
            lineCount += 1
        else:
            transactionVariables = formatTransactionVariables(account.name, row)
            # Skip transactions between automated accounts to prevent duplicates
            if transactionVariables[3]:
                continue
            else:
                description = modifyTransactionDescription(transactionVariables[1])
                postDate = transactionVariables[0].date()
                fromAccount = transactionVariables[4]
                amount = transactionVariables[2]
                toAccount = setToAccount(account.name, row)
                if 'ARCADIA' in description.upper():
                    energyBillNum += 1
                    amount = getEnergyBillAmounts(driver, transactionVariables[2], energyBillNum)
                elif 'NM PAYCHECK' in description.upper() or "CRYPTO PURCHASE" in description.upper():
                    reviewTrans = reviewTrans + transactionVariables[5]
                else:
                    if toAccount == "Expenses:Other":
                        
                        reviewTrans = reviewTrans + transactionVariables[5]
                writeGnuTransaction(myBook, description, postDate, amount, fromAccount, toAccount)
    account.updateGnuBalance(myBook)
    account.setReviewTransactions(reviewTrans)
    
def importUniqueTransactionsToGnuCash(account, transactionsCSV, driver, dateRange, lineStart=1):
    directory = setDirectory()
    importCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\import.csv"
    open(importCSV, 'w', newline='').truncate()
    myBook = openGnuCashBook('Finance', False, False)
    if account == 'Ally':
        gnuAccount = "Assets:Ally Checking Account"
        gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_ally.csv"
        myBook = openGnuCashBook('Home', False, False)
    elif account == 'Sofi Checking':
        gnuAccount = "Assets:Liquid Assets:Sofi:Checking"
        gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_sofi.csv"
    elif account == 'Sofi Savings':
        gnuAccount = "Assets:Liquid Assets:Sofi:Savings"
        gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_sofi.csv"
    open(gnuCSV, 'w', newline='').truncate()
    # retrieve transactions from GnuCash for the same date range
    transactions = [tr for tr in myBook.transactions
                    if tr.post_date >= dateRange[0] and tr.post_date <= dateRange[1]
                    for spl in tr.splits
                    if spl.account.fullname == gnuAccount]
    for tr in transactions:
        date = str(tr.post_date.strftime('%Y-%m-%d'))
        description = str(tr.description)
        for spl in tr.splits:
            amount = format(spl.value, ".2f")
            if spl.account.fullname == gnuAccount:
                row = date, description, str(amount)
                csv.writer(open(gnuCSV, 'a', newline='')).writerow(row)
    for row in csv.reader(open(transactionsCSV, 'r'), delimiter=','):
        if row not in csv.reader(open(gnuCSV, 'r'), delimiter=','):
            csv.writer(open(importCSV, 'a', newline='')).writerow(row)
    importGnuTransaction(account, importCSV, myBook, driver, lineStart)

def writeGnuTransaction(myBook, description, postDate, amount, fromAccount, toAccount=''):
    with myBook as book:
        if "Contribution + Interest" in description:
            split = [Split(value=amount[0], memo="scripted", account=myBook.accounts(fullname="Income:Investments:Interest")),
                    Split(value=amount[1], memo="scripted",account=myBook.accounts(fullname="Income:Employer Pension Contributions")),
                    Split(value=amount[2], memo="scripted",account=myBook.accounts(fullname=fromAccount))]
        elif "HSA Statement" in description:
            if amount[1]:
                split = [Split(value=amount[0], account=myBook.accounts(fullname=toAccount)),
                        Split(value=amount[1], account=myBook.accounts(fullname=fromAccount[0])),
                        Split(value=amount[2], account=myBook.accounts(fullname=fromAccount[1]))]
            else:
                split = [Split(value=amount[0], account=myBook.accounts(fullname=toAccount)),
                        Split(value=amount[2], account=myBook.accounts(fullname=fromAccount[1]))]
        elif "ARCADIA" in description:
            split=[Split(value=amount[0], memo="Arcadia Membership Fee", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=amount[1], memo="Solar Rebate", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=amount[2], account=myBook.accounts(fullname="Expenses:Utilities:Electricity")),
                    Split(value=amount[3], account=myBook.accounts(fullname="Expenses:Utilities:Gas")),
                    Split(value=amount[4], account=myBook.accounts(fullname=fromAccount))]
        elif "NM Paycheck" in description:
            split = [Split(value=round(Decimal(2160.53), 2), memo="scripted",account=myBook.accounts(fullname=fromAccount)),
                    Split(value=round(Decimal(274.67), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:401k")),
                    Split(value=round(Decimal(5.49), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Dental")),
                    Split(value=round(Decimal(34.10), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Health")),
                    Split(value=round(Decimal(2.67), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Vision")),
                    Split(value=round(Decimal(202.39), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Social Security")),
                    Split(value=round(Decimal(47.33), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Medicare")),
                    Split(value=round(Decimal(415.83), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Federal Tax")),
                    Split(value=round(Decimal(159.07), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:State Tax")),
                    Split(value=round(Decimal(131.25), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:HSA:NM HSA")),
                    Split(value=-round(Decimal(3433.33), 2), memo="scripted",account=myBook.accounts(fullname=toAccount))]
        else:
            split = [Split(value=-amount, memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=amount, memo="scripted", account=myBook.accounts(fullname=fromAccount))]
        Transaction(post_date=postDate, currency=myBook.currencies(mnemonic="USD"), description=description, splits=split)
        book.save()
        book.flush()
    book.close()
    
def updateCryptoPriceInGnucash(symbol, coinPrice):
    myBook = openGnuCashBook('Finance', False, False)
    try: 
        gnuCashPrice = myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=datetime.today().date())  # raise a KeyError if Price does not exist
        gnuCashPrice.value = coinPrice
    except KeyError:
        p = Price(myBook.commodities(mnemonic=symbol), myBook.currencies(mnemonic="USD"), datetime.today().date(), coinPrice, "last")
    myBook.save()
    myBook.close()

def getDollarsInvestedPerCoin(name):
    # get dollars invested balance (must be run per coin)
    mybook = openGnuCashBook('Finance', True, True)
    gnu_account = getAccountPath(name)
    total = 0
    # retrieve transactions from GnuCash
    transactions = [tr for tr in mybook.transactions
                    for spl in tr.splits
                    if spl.account.fullname == gnu_account]
    for tr in transactions:
        for spl in tr.splits:
            amount = format(spl.value, ".2f")
            if spl.account.fullname == gnu_account:
                total += abs(float(amount))
    print(f'total $ invested in {name}: ' + str(total))
    return total            

def purgeOldGnucashFiles():
    directory = setDirectory()
    today = datetime.today()
    dateRange = getStartAndEndOfDateRange(today, today.month, today.year, 14)
    directories = [directory + r'\Finances\Personal Finances', directory + r'\Stuff\Home\Finances']
    for d in directories:
        directory = d
        for fileName in listdir(directory):
            filePath = (directory + r'\'' + fileName).replace("'",'')
            fileModifiedDate = datetime.fromtimestamp(os.path.getmtime(filePath)).date()
            if fileModifiedDate < dateRange[0]:
                os.remove(filePath)
