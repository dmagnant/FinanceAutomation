import time, csv
from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Optum":
    from Classes.Asset import USD, Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            showMessage, setDirectory, getUsername, getPassword, getAnswerForSecurityQuestion)
else:
    from .Classes.Asset import USD, Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             showMessage, setDirectory, getUsername, getPassword, getAnswerForSecurityQuestion)  
    
def locateOptumWindow(driver):
    found = driver.findWindowByUrl("secure.optumfinancial.com")
    if not found:   optumLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    
# def answerOptumSecurityQuestions(driver):
#     question = driver.getElementText('xpath', "//*[@id='answer-0_container']/div[1]/label/span")
#     print(question)
#     driver.getElementAndSendKeys('id', 'answer-0', getAnswerForSecurityQuestion(question))
#     driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/div[3]/div/div[2]/form/div/div[2]/div") # Trust this device
#     driver.getElementAndClick('id', "submitBtn") # Continue
        
def optumLogin(driver):
    driver.openNewWindow('https://secure.optumfinancial.com/portal/hsid/login?url=/portal/CC')
    if driver.getElementAndSendKeys('id', 'username', getUsername('Optum HSA')):
        driver.getElementAndSendKeys('id', 'password', getPassword('Optum HSA'))
        time.sleep(1)
        driver.getElementAndClick('id', 'submitBtn') # Sign in
    
def getOptumBalance(driver, accounts):
    locateOptumWindow(driver)
    optumPostLoginPageURL = "https://secure.optumfinancial.com/portal/CC/cdhportal"
    if not driver.webDriver.current_url == optumPostLoginPageURL:   driver.webDriver.get(optumPostLoginPageURL)
    cashBalance = driver.getElementText('id', "availableToSpendBoxValue", allowFail=False)
    vfiaxBalance = driver.getElementText('id', "investmentBalance", allowFail=False)
    if cashBalance and vfiaxBalance:
        accounts['OptumCash'].setBalance(cashBalance.replace("$","").replace(",",""))
        accounts['VFIAX'].setValue(vfiaxBalance.replace("$","").replace(",",""))
    else:
        return

def getOptumPricesSharesAndCost(driver, accounts, book):
    locateOptumWindow(driver)
    optumInvestPageURL = "https://secure.optumfinancial.com/portal/CC/cdhportal/cdhaccount/investcenter"
    if not driver.webDriver.current_url == optumInvestPageURL:  driver.webDriver.get(optumInvestPageURL)
    price = driver.getElementText('xpath', "//*[@id='investCenter']/div[4]/div/div[1]/div[2]/div/table/tbody/tr[1]/td[4]", allowFail=False)
    balance = driver.getElementText('xpath', "//*[@id='investCenter']/div[4]/div/div[1]/div[2]/div/table/tbody/tr[1]/td[3]", allowFail=False)
    if price and balance:
        accounts['VFIAX'].price = price.replace("$","").replace(",","")
        book.updatePriceInGnucash(accounts['VFIAX'].symbol, accounts['VFIAX'].price)
        accounts['VFIAX'].setBalance(balance.replace(",",""))
        accounts['VFIAX'].cost = book.getDollarsInvestedPerSecurity(accounts['VFIAX'])
    
def setOptumTransactionPath(row, column):    return f"//*[@id='trans']/tbody/tr[{str(row)}]/td[{str(column)}]"

def captureOptumTransactions(driver, lastMonth):
    locateOptumWindow(driver)
    optumActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\optum.csv"
    open(optumActivity, 'w', newline='').truncate()
    row = 0
    if "investcenter" not in driver.webDriver.current_url:
        driver.getElementAndClick('xpath', "//*[@id='investmentBox']/a") # Investments
    driver.getElementAndClick('xpath', "//*[@id='invest-center-submenu']/li[2]/a") # Investment Transactions
    driver.getElementAndClick('xpath', "//*[@id='investCenter']/div[3]/div[1]/div/div/a") # View all settled Transactions
    driver.getElementAndSendKeys('id', "startDate", lastMonth['startDate'].strftime('%m/%d/%Y'))
    driver.getElementAndSendKeys('id', "endDate", lastMonth['endDate'].strftime('%m/%d/%Y'))
    driver.getElementAndClick('xpath', "//*[@id='customDates']/div[4]/input") # Search
    while True:
        row+=1
        column = 1
        dateElement = driver.getElement('xpath', setOptumTransactionPath(row, column), wait=5)
        if not dateElement:
            if row==1:  showMessage('Error finding Date Element', 'Element path for date element has changed, please update.')
            break
        date = datetime.strptime(dateElement.text, '%m/%d/%Y').date()
        if date.month == lastMonth['endDate'].month:
            column+=1
            description = driver.getElementText('xpath', setOptumTransactionPath(row, column))
            column+=1
            description += " " + driver.getElementText('xpath',setOptumTransactionPath(row, column))
            column+=1
            shares = driver.getElementText('xpath',setOptumTransactionPath(row, column))
            column+=2
            rawAmount = driver.getElementText('xpath',setOptumTransactionPath(row, column))
            if rawAmount:
                amount = rawAmount.replace('$','').replace(',','')
            transaction = date, description, shares, amount
            csv.writer(open(optumActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
        elif date.month < lastMonth['endDate'].month or date.year < lastMonth['endDate'].year:  break
    return optumActivity

def getOptumAccounts(book):
    return {'VFIAX': Security("VFIAX", book), 'OptumCash': USD("Optum Cash", book)}

def importOptumTransactions(account, optumActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(optumActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1]
        description = rawDescription        
        fromAccount = account.gnuAccount
        shares = float(row[2])
        amount = Decimal(row[3])
        toAccount = book.getGnuAccountFullName('Other')
        if "Vanguard 500 Index Admiral" in rawDescription:  
            if "FEE" in rawDescription.upper():
                description = "HSA Fee"
                amount,shares = -amount,-shares
                toAccount = book.getGnuAccountFullName('Bank Fees')
            elif "DIVIDEND" in rawDescription.upper():
                description = "HSA Dividend"
                toAccount = book.getGnuAccountFullName('Dividends')
            else:   
                description = "HSA VFIAX Investment"
                toAccount = book.getGnuAccountFullName('Optum Cash')
        # toAccount = book.getGnuAccountFullName(fromAccount, description=description)
        splits = [{'amount': -amount, 'account':toAccount},{'amount': amount, 'account':fromAccount, 'quantity': round(Decimal(shares),3)}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

def runOptum(driver, accounts, book, gnuCashTransactions, lastMonth):
    locateOptumWindow(driver)
    getOptumBalance(driver, accounts)
    getOptumPricesSharesAndCost(driver, accounts, book)
    optumActivity = captureOptumTransactions(driver, lastMonth)
    importOptumTransactions(accounts['VFIAX'], optumActivity, book, gnuCashTransactions)
    accounts['VFIAX'].setCost(book.getDollarsInvestedPerSecurity(accounts['VFIAX']))
    accounts['OptumCash'].updateGnuBalance(book.getGnuAccountBalance(accounts['OptumCash'].gnuAccount))
    accounts['VFIAX'].updateGnuBalanceAndValue(book.getGnuAccountBalance(accounts['VFIAX'].gnuAccount))
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    locateOptumWindow(driver)
    # accounts = getOptumAccounts(book)
    # lastMonth = getStartAndEndOfDateRange(timeSpan="month")
    # gnuCashTransactions = book.getTransactionsByDateRange(lastMonth)
    # getOptumBalance(driver, accounts)
    # getOptumPricesSharesAndCost(driver, accounts, book)
    # optumActivity = captureOptumTransactions(driver, lastMonth)
    # importOptumTransactions(accounts['VFIAX'], optumActivity, book, gnuCashTransactions)
    # accounts['VFIAX'].setCost(book.getDollarsInvestedPerSecurity(accounts['VFIAX']))
    # accounts['OptumCash'].updateGnuBalance(book.getGnuAccountBalance(accounts['OptumCash'].gnuAccount))
    # accounts['VFIAX'].updateGnuBalanceAndValue(book.getGnuAccountBalance(accounts['VFIAX'].gnuAccount))    
    # book.closeBook()