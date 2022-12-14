import csv
import os
import time
from datetime import datetime
from decimal import Decimal
from os import listdir

import piecash
from piecash import GnucashException, Price, Split, Transaction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .GeneralFunctions import (closeExpressVPN, getPassword,
                               getStartAndEndOfDateRange, getUsername,
                               setDirectory, showMessage)

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
        case 'Sofi Checking':
            return "Assets:Liquid Assets:Sofi:Checking"
        case 'Sofi Savings':
            return "Assets:Liquid Assets:Sofi:Savings"                
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Bonds:Worthy Bonds"
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')

def importGnuTransaction(account, transactionsCSV, driver, lineStart=1):
    def setToAccount(account, row):
        toAccount = ''
        rowNum = 2 if account in ['BoA', 'BoA-joint', 'Chase', 'Discover'] else 1
        if "BoA CC" in row[rowNum]:
            if "Rewards" in row[rowNum]:
                toAccount = "Income:Credit Card Rewards"  
            else: 
                if account == 'Ally':
                    toAccount = "Liabilities:BoA Credit Card"
                elif "Sofi" in account:
                    toAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"        
        elif "ARCADIA" in row[rowNum]:
            toAccount = ""
        elif "Interest earned" in row[rowNum]:
            toAccount = "Income:Investments:Interest"
        elif "Savings Transfer" in row[rowNum]:
            toAccount = "Assets:Liquid Assets:Sofi:Savings"        
        elif "Tessa Deposit" in row[rowNum]:
            toAccount = "Tessa's Contributions"
        elif "Jonny payment" in row[rowNum]:
            toAccount = "Liabilities:Loans:Personal Loan"
        elif "MyConstant transfer" in row[rowNum]:
            toAccount = "Assets:Liquid Assets:My Constant"
        elif "Water Bill" in row[rowNum]:
            toAccount = "Expenses:Utilities:Water"
        elif "Dan Deposit" in row[rowNum]:
            toAccount = "Dan's Contributions"
        elif "Mortgage Payment" in row[rowNum]:
            toAccount = "Liabilities:Mortgage Loan"
        elif "Swagbucks" in row[rowNum]:
            toAccount = "Income:Market Research"
        elif "NM Paycheck" in row[rowNum]:
            toAccount = "Income:Salary"
        elif "GOOGLE FI" in row[rowNum].upper() or "GOOGLE *FI" in row[rowNum].upper():
            toAccount = "Expenses:Utilities:Phone"
        elif "Alliant Transfer" in row[rowNum]:
            toAccount = "Assets:Liquid Assets:Promos:Alliant"        
        elif "CRYPTO PURCHASE" in row[rowNum].upper():
            toAccount = "Assets:Non-Liquid Assets:CryptoCurrency"
        elif "Pinecone Research" in row[rowNum]:
            toAccount = "Income:Market Research"
        elif "Internet Bill" in row[rowNum]:
            toAccount = "Expenses:Utilities:Internet"
        elif "IRA Transfer" in row[rowNum]:
            toAccount = "Assets:Non-Liquid Assets:Roth IRA"
        elif "Lending Club" in row[rowNum]:
            toAccount = "Income:Investments:Interest"
        elif "CASH REWARDS STATEMENT CREDIT" in row[rowNum]:
            toAccount = "Income:Credit Card Rewards"        
        elif "Chase CC Rewards" in row[rowNum]:
            toAccount = "Income:Credit Card Rewards"
        elif "Chase CC" in row[rowNum]:
            toAccount = "Liabilities:Credit Cards:Chase Freedom"
        elif "Discover CC Rewards" in row[rowNum]:
            toAccount = "Income:Credit Card Rewards"        
        elif "Discover CC" in row[rowNum]:
            toAccount = "Liabilities:Credit Cards:Discover It"
        elif "Amex CC" in row[rowNum]:
            toAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
        elif "Barclays CC Rewards" in row[rowNum]:
            toAccount = "Income:Credit Card Rewards"
        elif "Barclays CC" in row[rowNum]:
            toAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
        elif "Ally Transfer" in row[rowNum]:
            toAccount = "Expenses:Joint Expenses"    
        elif "BP#" in row[rowNum]:
            toAccount = "Expenses:Transportation:Gas (Vehicle)"
        elif "CAT DOCTOR" in row[rowNum]:
            toAccount = "Expenses:Medical:Vet"
        elif "PARKING" in row[rowNum] or "SPOTHERO" in row[rowNum].upper():
            toAccount = "Expenses:Transportation:Parking"
        elif "PROGRESSIVE" in row[rowNum]:
            toAccount = "Expenses:Transportation:Car Insurance"
        elif "CHARTER SERVICES" in row[rowNum].upper():
                toAccount = "Expenses:Utilities:Internet"     
        elif "UBER" in row[rowNum].upper() and "EATS" in row[rowNum].upper():
            toAccount = "Expenses:Bars & Restaurants"
        elif "UBER" in row[rowNum].upper():
            toAccount = "Expenses:Travel:Ride Services" if account in ['BoA-joint', 'Ally'] else "Expenses:Transportation:Ride Services"
        elif "TECH WAY AUTO SERV" in row[rowNum].upper():
            toAccount = "Expenses:Transportation:Car Maintenance"
        elif "INTEREST PAID" in row[rowNum].upper():
            toAccount = "Income:Interest" if account in ['BoA-joint', 'Ally'] else "Income:Investments:Interest"
        if not toAccount:
            for i in ['HOMEDEPOT.COM', 'HOME DEPOT']:
                if i in row[rowNum].upper():
                    if account in ['BoA-joint', 'Ally']:
                        toAccount = "Expenses:Home Depot"
        
        if not toAccount:
            for i in ['AMAZON', 'AMZN']:
                if i in row[rowNum].upper():
                    toAccount = "Expenses:Amazon"

        if not toAccount:
            if len(row) >= 5:
                if row[3] == "Groceries" or row[4] == "Supermarkets":
                    toAccount = "Expenses:Groceries"
            if not toAccount:
                for i in ['PICK N SAVE', 'KETTLE RANGE', 'WHOLE FOODS', 'WHOLEFDS', 'TARGET']:
                    if i in row[rowNum].upper():
                        toAccount = "Expenses:Groceries"

        if not toAccount:
            if len(row) >= 5:
                if row[3] == "Food & Drink" or row[4] == "Restaurants":
                    toAccount = "Expenses:Bars & Restaurants"
            if not toAccount:
                for i in ['MCDONALD', 'GRUBHUB', 'JIMMY JOHN', 'COLECTIVO', 'INSOMNIA', 'EATSTREET', "KOPP'S CUSTARD", 'MAHARAJA', 'STARBUCKS', "PIETRO'S PIZZA", 'SPROCKET CAFE']:
                    if i in row[rowNum].upper():
                        toAccount = "Expenses:Bars & Restaurants"
        
        if not toAccount:
            toAccount = "Expenses:Other"
        return toAccount
    def formatTransactionVariables(account, row):
        skipTransaction = False
        description = row[1]
        if account == 'Ally':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            amount = Decimal(row[2])
            fromAccount = "Assets:Ally Checking Account"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
        elif account == 'Amex':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[1]
            amount = -Decimal(row[2])
            if "AUTOPAY PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
        elif account == 'Barclays':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[1]
            amount = Decimal(row[3])
            if "PAYMENT RECEIVED" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[3] + "\n"
        elif account == 'BoA':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[4])
            if "BA ELECTRONIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"
            reviewTransPath = row[0] + ", " + row[2] + ", " + row[4] + "\n"
        elif account == 'BoA-joint':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[4])
            if "BA ELECTRONIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:BoA Credit Card"
            reviewTransPath = row[0] + ", " + row[2] + ", " + row[4] + "\n"
        elif account == 'Chase':
            postDate = datetime.strptime(row[1], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[5])
            if "AUTOMATIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Chase Freedom"
            reviewTransPath = row[1] + ", " + row[2] + ", " + row[5] + "\n"
        elif account == 'Discover':
            postDate = datetime.strptime(row[1], '%m/%d/%Y')
            description = row[2]
            amount = -Decimal(row[3])
            if "DIRECTPAY FULL BALANCE" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Discover It"
            reviewTransPath = row[1] + ", " + row[2] + ", " + row[3] + "\n"
        elif account == 'Sofi Checking':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            amount = Decimal(row[2])
            fromAccount = "Assets:Liquid Assets:Sofi:Checking"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"
        elif account == 'Sofi Savings':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            if "CHECKING - 6915" in description.upper():
                skipTransaction = True
            amount = Decimal(row[2])
            fromAccount = "Assets:Liquid Assets:Sofi:Savings"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2] + "\n"        
        return [postDate, description, amount, skipTransaction, fromAccount, reviewTransPath]
    def getEnergyBillAmounts(driver, amount, energyBillNum):
        directory = setDirectory()
        if energyBillNum == 1:
            closeExpressVPN()
            driver.execute_script("window.open('https://login.arcadia.com/email');")
            driver.implicitly_wait(5)
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            # get around bot-prevention by logging in twice
            num = 1
            while num <3:
                try:
                    # click Sign in with email
                    driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/div/div[1]/div/a").click()
                    time.sleep(1)
                except NoSuchElementException:
                    exception = "sign in page loaded already"
                try:
                    # Login
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[1]/div[1]/input").send_keys(getUsername(directory, 'Arcadia Power'))
                    time.sleep(1)
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[1]/div[2]/input").send_keys(getPassword(directory, 'Arcadia Power'))
                    time.sleep(1)
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/form/div[2]/button").click()
                    time.sleep(1)
                    # Get Billing page
                    driver.get("https://home.arcadia.com/dashboard/2072648/billing")
                except NoSuchElementException:
                    exception = "already signed in"
                try: 
                    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[1]/h1')
                    num = 4
                except NoSuchElementException:
                    num += 1
            if num == 3:
                showMessage("Login Check", 'Confirm Login to Arcadia, (manually if necessary) \n' 'Then click OK \n')
        else:
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            driver.get("https://home.arcadia.com/dashboard/2072648/billing")
        statementRow = 1
        statementFound = "no"                     
        while statementFound == "no":
            # Capture statement balance
            arcadiaBalance = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/li[" + str(statementRow) + "]/div[2]/div[2]/div[1]/div/p")
            formattedAmount = "{:.2f}".format(abs(amount))
            if arcadiaBalance.text.strip('$') == formattedAmount:
                # click to view statement
                arcadiaBalance.click()
                statementFound = "yes"
            else:
                statementRow += 1
        # comb through lines of Arcadia Statement for Arcadia Membership (and Free trial rebate), Community Solar lines (3)
        arcadiaStatementLinesLeft = True
        statementRow = 1
        solar = 0
        arcadiaMembership = 0
        while arcadiaStatementLinesLeft:
            try:
                # read the header to get transaction description
                statementTrans = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/h2").text
                if statementTrans == "Arcadia Membership":
                    arcadiaMembership = Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
                    arcadiaamt = Decimal(arcadiaMembership)
                elif statementTrans == "Free Trial":
                    arcadiaMembership = arcadiaMembership + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
                elif statementTrans == "Community Solar":
                    solar = solar + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.replace('$',''))
                elif statementTrans == "WE Energies Utility":
                    weBill = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text
                statementRow += 1
            except NoSuchElementException:
                arcadiaStatementLinesLeft = False
        arcadiaamt = Decimal(arcadiaMembership)
        solarAmount = Decimal(solar)
        # Get balances from WE Energies
        if energyBillNum == 1:
            driver.execute_script("window.open('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx');")
            # switch to last window
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            try:
                ## LOGIN
                driver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername(directory, 'WE-Energies (Home)'))
                driver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword(directory, 'WE-Energies (Home)'))
                # click Login
                driver.find_element(By.XPATH, "//*[@id='next']").click()
                time.sleep(4)
                # close out of app notice
                driver.find_element(By.XPATH, "//*[@id='notInterested']/a").click
            except NoSuchElementException:
                exception = "caught"
            # Click View bill history
            driver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click()
            time.sleep(4)
        billRow = 2
        billColumn = 7
        billFound = "no"
        # find bill based on comparing amount from Arcadia (weBill)
        while billFound == "no":
            # capture date
            weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
            weBillAmount = driver.find_element(By.XPATH, weBillPath).text
            if weBill == weBillAmount:
                billFound = "yes"
            else:
                billRow += 1
        # capture gas charges
        billColumn -= 2
        weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
        gasAmount = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
        # capture electricity charges
        billColumn -= 2
        weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
        electricityAmount = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
        return [arcadiaamt, solarAmount, electricityAmount, gasAmount, amount]

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
    if account.name == 'Ally':
        gnuAccount = "Assets:Ally Checking Account"
        gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_ally.csv"
        myBook = openGnuCashBook('Home', False, False)
    elif account.name == 'Sofi Checking':
        gnuAccount = "Assets:Liquid Assets:Sofi:Checking"
        gnuCSV = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\gnu_sofi.csv"
    elif account.name == 'Sofi Savings':
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
    importGnuTransaction(account, importCSV, driver, lineStart)

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

def consolidatePastTransactions(myBook, fromAccount, toAccount, description):
    def loopPerYear(allTransactions, date, toAccount, fromAccount, myBook, description):
        today = datetime.today()
        while today.year - date.year >= 1:
            transInYear = []
            for trans in allTransactions:
                if trans.post_date.year == date.year:
                    transInYear.append(trans)
            if len(transInYear) > 1:
                total = 0
                for tr in transInYear:
                    for spl in tr.splits:
                        if spl.account.fullname == toAccount:
                            total += spl.value
                    myBook.delete(tr)
                split = [Split(value=total, memo="scripted", account=myBook.accounts(fullname=toAccount)),
                         Split(value=-total, memo="scripted", account=myBook.accounts(fullname=fromAccount))]
                Transaction(post_date=date, currency=myBook.currencies(mnemonic="USD"), description=description, splits=split)
                myBook.save()
                myBook.flush()
            date = date.replace(year=date.year+1)
            
    transactions = []
    for transaction in myBook.transactions:
        account1 = transaction.splits[0].account.fullname
        account2 = transaction.splits[1].account.fullname
        if (account1 == toAccount or account1 == fromAccount) and (account2 == toAccount or account2 == fromAccount):
            transactions.append(transaction)
    startDate = transactions[0].post_date.replace(month=12, day=31)
    loopPerYear(transactions, startDate, toAccount, fromAccount, myBook, description)
    myBook.close()
    
def modifyTransactionDescription(description, amount="0.00"):
    if "INTERNET TRANSFER FROM ONLINE SAVINGS ACCOUNT XXXXXX9703" in description.upper():
        description = "Tessa Deposit"
    elif "INTEREST EARNED" in description.upper():
        description = "Interest earned"
    elif "SOFI REWARDS REDEMPTION" in description.upper():
        description = "Interest earned"
    elif "JONATHON MAGNANT" in description.upper():
        description = "Jonny payment"
    elif "SAVINGS - 3467" in description.upper():
        description = "Savings Transfer"
    elif "ALLY BANK TRANSFER" in description.upper():
        description = "Dan Deposit"
    elif "ALLY BANK" in description.upper():
        description = "Ally Transfer"
    elif "M1 FINANCE" in description.upper():
        description = "IRA Transfer"
    elif "CITY OF MILWAUKE B2P*MILWWA" in description.upper():
        description = "Water Bill"
    elif "DOVENMUEHLE MTG MORTG PYMT" in description.upper():
        description = "Mortgage Payment"
    elif "NORTHWESTERN MUT" in description.upper():
        description = "NM Paycheck"
    elif "PAYPAL" in description.upper() and "10.00" in amount:
        description = "Swagbucks"  
    elif "PAYPAL" in description.upper():
        description = "Paypal"
    elif "NIELSEN" in description.upper() and "3.00" in amount:
        description = "Pinecone Research"
    elif "VENMO" in description.upper():
        description = "Venmo"
    elif "ALLIANT CU" in description.upper():
        description = "Alliant Transfer"        
    elif "AMEX EPAYMENT" in description.upper():
        description = "Amex CC"
    elif "SPECTRUM" in description.upper():
        description = "Internet Bill"
    elif "COINBASE" in description.upper():
        description = "Crypto purchase"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) > 0:
        description = "Chase CC Rewards"
    elif "CHASE CREDIT CRD" in description.upper() and float(amount) < 0:
        description = "Chase CC"
    elif "DISCOVER CASH AWARD" in description.upper():
        description = "Discover CC Rewards"        
    elif "DISCOVER" in description.upper():
        description = "Discover CC"
    elif "BARCLAYCARD US" in description.upper() and float(amount) > 0:
        description = "Barclays CC Rewards"
    elif "BARCLAYCARD US" in description.upper() and float(amount) < 0:
        description = "Barclays CC"        
    elif "BK OF AMER VISA" in description.upper():
        description = "BoA CC"
    elif "CASH REWARDS STATEMENT CREDIT" in description.upper():
        description = "BoA CC Rewards"
    return description

def openGnuCashUI(book):
    directory = setDirectory()
    if book == 'Finances':
        path = r"\Finances\Personal Finances\Finance.gnucash"
    elif book == 'Home':
        path = r"\Stuff\Home\Finances\Home.gnucash"
    elif book == 'Test':
        path = r"\Finances\Personal Finances\test.gnucash"
    os.startfile(directory + path)

def consolidatePastTransactionsWithSplits(myBook):
    def loopPerYear(allTransactions, date, myBook):
        today = datetime.today()
        while today.year - date.year >= 1:
            transInYear = []
            for trans in allTransactions:
                if trans.post_date.year == date.year:
                    transInYear.append(trans)
            if len(transInYear) > 1:
                sofi = 0
                rewards = 0
                grocery = 0
                for tr in transInYear:
                    for spl in tr.splits:                        
                        if spl.account.fullname == 'Assets:Liquid Assets:Sofi':
                            sofi += spl.value
                        elif spl.account.fullname == 'Income:Credit Card Rewards':
                            rewards += spl.value
                        elif spl.account.fullname == 'Expenses:Groceries':
                            grocery += spl.value                            
                    myBook.delete(tr)
                split = [Split(value=sofi, memo="scripted", account=myBook.accounts(fullname='Assets:Liquid Assets:Sofi')),
                         Split(value=rewards, memo="scripted", account=myBook.accounts(fullname='Income:Credit Card Rewards')),
                         Split(value=grocery, memo="scripted", account=myBook.accounts(fullname='Expenses:Groceries'))
                         ]
                Transaction(post_date=date, currency=myBook.currencies(mnemonic="USD"), description=str(date.year) + ' Checking Groceries', splits=split)
                myBook.save()
                myBook.flush()
            date = date.replace(year=date.year+1)
    transactions = []
    for transaction in myBook.transactions:
        if transaction.post_date.year == 2021:
            for spl in transaction.splits:
                if spl.account.fullname == 'Expenses:Groceries':
                    if transaction.description == "2021 grocery":
                        transactions.append(transaction)
    startDate = transactions[0].post_date.replace(month=12, day=31)
    loopPerYear(transactions, startDate, myBook)
    myBook.close()