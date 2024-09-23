import time
from datetime import datetime
from selenium.webdriver.common.by import By
from decimal import Decimal


if __name__ == '__main__' or __name__ == "AmazonGC":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash    
    from Functions.GeneralFunctions import showMessage
else:
    from .Classes.Asset import USD
    from .Classes.WebDriver import Driver    
    from .Classes.GnuCash import GnuCash    
    from .Functions.GeneralFunctions import showMessage

def locateAmazonWindow(driver):
    found = driver.findWindowByUrl("www.amazon.com/gc/balance")
    if not found:   driver.openNewWindow('https://www.amazon.com/gc/balance')
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def writeAmazonGCTransactionFromUI(book, account, requestInfo):
    if 'earn' in requestInfo:
        print('test')
        amount = Decimal(requestInfo['amount'])
        source = 'Income:Market Research:' + requestInfo['source']
    elif 'spend' in requestInfo:
        amount = -Decimal(requestInfo['amount'])
        source = book.getGnuAccount('Amazon') if 'Joint' not in requestInfo['source'] else book.getGnuAccount('Joint Expenses')
    else:   showMessage('Error', 'Missing proper header to submit this transaction from UI')
    description = requestInfo['description'] if requestInfo['description'] else requestInfo['source']
    transactionInfo = {'amount': amount, 'toAccount': account.gnuAccount.fullname, 'fromAccount': source, 'date': datetime.today().date(),'description': description}
    book.writeSimpleTransaction(transactionInfo)
    account.reviewTransactions = [source + ': ' + str(amount)]
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))
    if 'Joint' in requestInfo['source']:
        jointBook = GnuCash('Home')
        transactionInfo = {'amount': amount, 'toAccount': jointBook.getGnuAccountName("Dan's Contributions"), 'fromAccount': jointBook.getGnuAccountName('Amazon'), 'date': datetime.today().date(),'description': description}
        jointBook.writeSimpleTransaction(transactionInfo)
        jointBook.closeBook()
    confirmAmazonGCBalance(Driver("Chrome"), account)

def confirmAmazonGCBalance(driver, account):
    locateAmazonWindow(driver)
    balance = driver.webDriver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$')
    if float(balance) == 0: balance = "0"
    account.setBalance(balance)
    if str(account.gnuBalance) != account.balance:  showMessage("Amazon GC Mismatch", f'Amazon balance: {account.balance} \n' f'Gnu Cash balance: {account.gnuBalance} \n')

# if __name__ == '__main__':
#     book = GnuCash('Finance')
#     driver = Driver("Chrome")
#     AmazonGC = USD("Amazon GC", book)    
#     confirmAmazonGCBalance(driver, AmazonGC)
#     AmazonGC.getData()
#     book.closeBook()

if __name__ == '__main__':
    book = GnuCash('Finance')
    AmazonGC = USD("Amazon GC", book)
    AmazonGC.getData()
#     # addAmazonGCAmount(book, AmazonGC, Decimal(10.00), 'Pinecone'), book.closeBook()
    