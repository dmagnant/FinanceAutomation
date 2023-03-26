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

from .GeneralFunctions import (closeExpressVPN, getPassword,
                               getStartAndEndOfDateRange, getUsername,
                               setDirectory, showMessage)

def openGnuCashBook(type, readOnly, openIfLocked):
    if type == 'Finance':
        bookPathSuffix = r"\Finances\Personal Finances\Finance.gnucash"
    elif type == 'Home':
        bookPathSuffix = r"\Stuff\Home\Finances\Home.gnucash"
    elif type == 'Test':
        bookPathSuffix = r"\Finances\Personal Finances\test.gnucash"
    book = setDirectory() + bookPathSuffix
    try:
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked, check_same_thread=False)
    except GnucashException:
        showMessage("Gnucash file open", f'Close Gnucash file then click OK \n')
        myBook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked, check_same_thread=False)
    return myBook

def getGnuCashBalance(myBook, accountPath):
    balance = myBook.accounts(fullname=accountPath).get_balance()
    if balance == 0:
        balance = (str(balance).replace('-', ''))
    return balance

def getAccountPath(account):
    if account.account != None:
        accountName = account.account
    else:
        accountName = account.name
    match accountName:
        case 'Cardano':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano"
        case 'ADA-Eternl':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano:ADA-Eternl"    
        case 'ADA-Nami':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Cardano:ADA-Nami"    
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
        case 'ETH-Ledger':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum:ETH-Ledger"
        case 'Ethereum2':
            return "Assets:Non-Liquid Assets:CryptoCurrency:Ethereum2"
        case 'Fidelity':
            return "Assets:Non-Liquid Assets:IRA:Fidelity"
        case 'HSA':
            return "Assets:Non-Liquid Assets:HSA:NM HSA"
        case 'Home':
            return "Liabilities:Mortgage Loan"
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
        case 'Vanguard401k':
            return "Assets:Non-Liquid Assets:401k"                         
        case 'VanguardPension':
            return "Assets:Non-Liquid Assets:Pension"  
        case 'Worthy':
            return "Assets:Liquid Assets:Bonds:Worthy Bonds"
        case 'Bing':
            return "Assets:Non-Liquid Assets:MR:Bing"
        case 'Paidviewpoint':
            return "Assets:Non-Liquid Assets:MR:Paidviewpoint"        
        case 'Pinecone':
            return "Assets:Non-Liquid Assets:MR:Pinecone"
        case 'Swagbucks':
            return "Assets:Non-Liquid Assets:MR:Swagbucks"
        case 'Tellwut':
            return "Assets:Non-Liquid Assets:MR:Tellwut"
        case _:
            print(f'account: {accountName} not found in "getAccountPath" function')

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
    elif "FID BKG SVC LLC" in description.upper():
        description = "Fidelity IRA Transfer"
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
        print('step 1: changed from spectrum to internet bill')
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

def importGnuTransaction(account, transactionsCSV, driver, lineStart=1):
    def setToAccount(account, description):
        toAccount = ''
        if "BoA CC" in description:
            if "Rewards" in description:
                toAccount = "Income:Credit Card Rewards"  
            else: 
                if account == 'Ally':
                    toAccount = "Liabilities:BoA Credit Card"
                elif "Sofi" in account:
                    toAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"        
        elif "ARCADIA" in description:
            toAccount = ""
        elif "Interest earned" in description:
            toAccount = "Income:Investments:Interest"
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
            toAccount = "Income:Market Research"
        elif "NM Paycheck" in description:
            toAccount = "Income:Salary"
        elif "GOOGLE FI" in description.upper() or "GOOGLE *FI" in description.upper():
            toAccount = "Expenses:Utilities:Phone"
        elif "Alliant Transfer" in description:
            toAccount = "Assets:Liquid Assets:Promos:Alliant"
        elif "KAINTH" in description:
            toAccount = "Expenses:Groceries"
        elif "MINI MARKET MILWAUKEE WI" in description:
            toAccount = "Expenses:Groceries"
        elif "CRYPTO PURCHASE" in description.upper():
            toAccount = "Assets:Non-Liquid Assets:CryptoCurrency"
        elif "Pinecone Research" in description:
            toAccount = "Income:Market Research"
        elif "Internet Bill" in description:
            toAccount = "Expenses:Utilities:Internet"
        elif "TRAVEL CREDIT" in description:
            toAccount = "Income:Credit Card Rewards"
        elif "Fidelity IRA Transfer" in description:
            toAccount = "Assets:Non-Liquid Assets:IRA:Fidelity"
        elif "MILWAUKEE ELECTRIC TO" in description:
            toAccount = "Expenses:Home Expenses:Maintenance"
        elif "CASH REWARDS STATEMENT CREDIT" in description:
            toAccount = "Income:Credit Card Rewards"        
        elif "Chase CC Rewards" in description:
            toAccount = "Income:Credit Card Rewards"
        elif "Chase CC" in description:
            toAccount = "Liabilities:Credit Cards:Chase Freedom"
        elif "Discover CC Rewards" in description:
            toAccount = "Income:Credit Card Rewards"        
        elif "Discover CC" in description:
            toAccount = "Liabilities:Credit Cards:Discover It"
        elif "Amex CC" in description:
            toAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
        elif "Barclays CC Rewards" in description:
            toAccount = "Income:Credit Card Rewards"
        elif "Barclays CC" in description:
            toAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
        elif "Ally Transfer" in description:
            toAccount = "Expenses:Joint Expenses"    
        elif "BP#" in description:
            toAccount = "Expenses:Transportation:Gas (Vehicle)"
        elif "CAT DOCTOR" in description:
            toAccount = "Expenses:Medical:Vet"
        elif "APPEN" in description:
            toAccount = "Income:Market Research"
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
        if account == 'Ally':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            amount = Decimal(row[2])
            fromAccount = "Assets:Ally Checking Account"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
        elif account == 'Amex':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[1]
            amount = -Decimal(row[2])
            if "AUTOPAY PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Amex BlueCash Everyday"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
        elif account == 'Barclays':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[1]
            amount = Decimal(row[3])
            if "PAYMENT RECEIVED" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:BarclayCard CashForward"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[3]
        elif account == 'BoA':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[4])
            if "BA ELECTRONIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:BankAmericard Cash Rewards"
            reviewTransPath = row[0] + ", " + row[2] + ", " + row[4]
        elif account == 'BoA-joint':
            postDate = datetime.strptime(row[0], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[4])
            if "BA ELECTRONIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:BoA Credit Card"
            reviewTransPath = row[0] + ", " + row[2] + ", " + row[4]
        elif account == 'Chase':
            postDate = datetime.strptime(row[1], '%m/%d/%Y')
            description = row[2]
            amount = Decimal(row[5])
            if "AUTOMATIC PAYMENT" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Chase Freedom"
            reviewTransPath = row[1] + ", " + row[2] + ", " + row[5]
        elif account == 'Discover':
            postDate = datetime.strptime(row[1], '%m/%d/%Y')
            description = row[2]
            amount = -Decimal(row[3])
            if "DIRECTPAY FULL BALANCE" in description.upper():
                skipTransaction = True
            fromAccount = "Liabilities:Credit Cards:Discover It"
            reviewTransPath = row[1] + ", " + row[2] + ", " + row[3]
        elif account == 'Sofi Checking':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            amount = Decimal(row[2])
            fromAccount = "Assets:Liquid Assets:Sofi:Checking"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
        elif account == 'Sofi Savings':
            postDate = datetime.strptime(row[0], '%Y-%m-%d')
            description = row[1]
            if "CHECKING - 6915" in description.upper():
                skipTransaction = True
            amount = Decimal(row[2])
            fromAccount = "Assets:Liquid Assets:Sofi:Savings"
            reviewTransPath = row[0] + ", " + row[1] + ", " + row[2]
        description = modifyTransactionDescription(description)
        return {
            'postDate': postDate.date(),
            'description': description,
            'amount': amount,
            'skipTransaction': skipTransaction,
            'fromAccount': fromAccount,
            'reviewTransPath': reviewTransPath,            
        }
        # [postDate, description, amount, skipTransaction, fromAccount, reviewTransPath]
    def getEnergyBillAmounts(driver, amount, energyBillNum):
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
                    # enter email
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div[2]/form/div[1]/div[1]/div/input").send_keys(getUsername('Arcadia Power'))
                    time.sleep(1)
                    # enter password
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div[2]/form/div[1]/div[2]/div/input").send_keys(getPassword('Arcadia Power'))
                    time.sleep(1)
                    # click sign in
                    driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div[2]/form/div[2]/button").click()
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
        solarAmount = 0
        arcadiaMembership = 0
        while arcadiaStatementLinesLeft:
            try:
                # read the header to get transaction description
                statementTrans = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/h2").text
                if statementTrans == "Arcadia Membership":
                    arcadiaMembership = Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
                    arcadia = Decimal(arcadiaMembership)
                elif statementTrans == "Free Trial":
                    arcadiaMembership = arcadiaMembership + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.strip('$'))
                elif statementTrans == "Community Solar":
                    solarAmount = solarAmount + Decimal(driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text.replace('$',''))
                elif statementTrans == "WE Energies Utility":
                    weBill = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[5]/ul/li[" + str(statementRow) + "]/div/p").text
                statementRow += 1
            except NoSuchElementException:
                arcadiaStatementLinesLeft = False
        arcadia = Decimal(arcadiaMembership)
        solar = Decimal(solarAmount)
        # Get balances from WE Energies
        if energyBillNum == 1:
            driver.execute_script("window.open('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx');")
            # switch to last window
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            try:
                ## LOGIN
                driver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername('WE-Energies (Home)'))
                driver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword('WE-Energies (Home)'))
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
        gas = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
        # capture electricity charges
        billColumn -= 2
        weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
        electricity = Decimal(driver.find_element(By.XPATH, weAmountPath).text.strip('$'))
        return {
            'arcadia': arcadia,
            'solar': solar,
            'electricity': electricity,
            'gas': gas,
            'total': amount,            
        }
        # [arcadia, solarAmount, electricity, gas, amount]

    book = 'Home' if (account.name == 'Ally' or account.name == 'BoA-joint') else 'Finance'
    myBook = openGnuCashBook(book, False, False)
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
            if transactionVariables['skipTransaction']:
                continue
            else:
                toAccount = setToAccount(account.name, transactionVariables['description'])
                if 'ARCADIA' in transactionVariables['description'].upper():
                    energyBillNum += 1
                    transactionVariables['amount'] = getEnergyBillAmounts(driver, transactionVariables['amount'], energyBillNum)
                elif 'NM PAYCHECK' in transactionVariables['description'].upper() or "CRYPTO PURCHASE" in transactionVariables['description'].upper() or toAccount == "Expenses:Other":
                    account.setReviewTransactions(transactionVariables['reviewTransPath'])
                writeGnuTransaction(myBook, transactionVariables, toAccount)
    account.updateGnuBalance(myBook)
    
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
                    if tr.post_date >= dateRange['startDate'] and tr.post_date <= dateRange['endDate']
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

def writeGnuTransaction(myBook, transactionVariables, toAccount=''):
    with myBook as book:
        if "Contribution + Interest" in transactionVariables['description']:
            split = [Split(value=transactionVariables['amount']['interest'], memo="scripted", account=myBook.accounts(fullname="Income:Investments:Interest")),
                    Split(value=transactionVariables['amount']['employerContribution'], memo="scripted",account=myBook.accounts(fullname="Income:Employer Contributions:Pension Contributions")),
                    Split(value=transactionVariables['amount']['accountChange'], memo="scripted",account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "HSA Statement" in transactionVariables['description']:
            if transactionVariables['amount']['HSADividends']:
                split = [Split(value=transactionVariables['amount']['change'], account=myBook.accounts(fullname=toAccount)),
                        Split(value=transactionVariables['amount']['HSADividends'], account=myBook.accounts(fullname="Income:Investments:Dividends")),
                        Split(value=transactionVariables['amount']['HEHSAMarketChange'], account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
            else:
                split = [Split(value=transactionVariables['amount']['change'], account=myBook.accounts(fullname=toAccount)),
                        Split(value=transactionVariables['amount']['HEHSAMarketChange'], account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "ARCADIA" in transactionVariables['description']:
            split=[Split(value=transactionVariables['amount']['arcadia'], memo="Arcadia Membership Fee", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=transactionVariables['amount']['solar'], memo="Solar Rebate", account=myBook.accounts(fullname="Expenses:Utilities:Arcadia Membership")),
                    Split(value=transactionVariables['amount']['electricity'], account=myBook.accounts(fullname="Expenses:Utilities:Electricity")),
                    Split(value=transactionVariables['amount']['gas'], account=myBook.accounts(fullname="Expenses:Utilities:Gas")),
                    Split(value=transactionVariables['amount']['total'], account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        elif "NM Paycheck" in transactionVariables['description']:
            split = [Split(value=round(Decimal(2037.85), 2), memo="scripted",account=myBook.accounts(fullname=transactionVariables['fromAccount'])),
                    Split(value=round(Decimal(412.00), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:401k")),
                    Split(value=round(Decimal(5.49), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Dental")),
                    Split(value=round(Decimal(35.47), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Health")),
                    Split(value=round(Decimal(2.93), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Medical:Vision")),
                    Split(value=round(Decimal(201.78), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Social Security")),
                    Split(value=round(Decimal(47.19), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Medicare")),
                    Split(value=round(Decimal(392.49), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:Federal Tax")),
                    Split(value=round(Decimal(158.55), 2), memo="scripted",account=myBook.accounts(fullname="Expenses:Income Taxes:State Tax")),
                    Split(value=round(Decimal(139.58), 2), memo="scripted",account=myBook.accounts(fullname="Assets:Non-Liquid Assets:HSA:NM HSA")),
                    Split(value=-round(Decimal(3433.33), 2), memo="scripted",account=myBook.accounts(fullname=toAccount))]
        else:
            split = [Split(value=-transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=toAccount)),
                    Split(value=transactionVariables['amount'], memo="scripted", account=myBook.accounts(fullname=transactionVariables['fromAccount']))]
        Transaction(post_date=transactionVariables['postDate'], currency=myBook.currencies(mnemonic="USD"), description=transactionVariables['description'], splits=split)
        book.save()
        book.flush()
        book.close()

def getPriceInGnucash(symbol, date=''):
    myBook = openGnuCashBook('Finance', True, True)
    if symbol == "ETH2":
        symbol = 'ETH'
    if date:
        price = ''
        while not price:
            try:
                price =  myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=date).value
            except KeyError:
                date = date - timedelta(days=1)
        return price
    else:
        return myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD")).value 

def updatePriceInGnucash(symbol, coinPrice):
    myBook = openGnuCashBook('Finance', False, False)
    try: 
        gnuCashPrice = myBook.prices(commodity=myBook.commodities(mnemonic=symbol), currency=myBook.currencies(mnemonic="USD"), date=datetime.today().date())  # raise a KeyError if Price does not exist
        gnuCashPrice.value = coinPrice
    except KeyError:
        p = Price(myBook.commodities(mnemonic=symbol), myBook.currencies(mnemonic="USD"), datetime.today().date(), coinPrice, "last")
    myBook.save()
    myBook.flush()
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
    dateRange = getStartAndEndOfDateRange(datetime.today().date(), 14)
    directories = [directory + r'\Finances\Personal Finances', directory + r'\Stuff\Home\Finances']
    for d in directories:
        for fileName in listdir(d):
            filePath = (d + r'\'' + fileName).replace("'",'')
            fileModifiedDate = datetime.fromtimestamp(os.path.getmtime(filePath)).date()
            if fileModifiedDate < dateRange['startDate']:
                os.remove(filePath)
    
def consolidatePastYearsTransactions(myBook):
    today = datetime.today().date()
    transDate = today.replace(month=12, day=31)
    year = 2007
    while year < today.year:
        transDate = transDate.replace(year=year)
        transactions = []
        accounts = []
        totalValues = []
        totalQuantities = []
        split = []
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
                split.append(Split(value=totalValues[i], quantity=totalQuantities[i], memo="", account=myBook.accounts(fullname=account)))
            else:
                split.append(Split(value=totalValues[i], memo="", account=myBook.accounts(fullname=account)))
        Transaction(post_date=transDate, currency=myBook.currencies(mnemonic="USD"), description=str(transDate.year) + ' Totals', splits=split)
        year += 1
        
    for transaction in myBook.transactions:
        for spl in transaction.splits:
            if spl.value == 0 and spl.quantity == 0:
                myBook.delete(spl)
    myBook.save()
    myBook.flush()
    myBook.close()

def openGnuCashUI(book):
    if book == 'Finances':
        path = r"\Finances\Personal Finances\Finance.gnucash"
    elif book == 'Home':
        path = r"\Stuff\Home\Finances\Home.gnucash"
    elif book == 'Test':
        path = r"\Finances\Personal Finances\test.gnucash"
    os.startfile(setDirectory() + path)

def getTotalOfAutomatedMRAccounts(myBook):
    mrTotal = 0
    swagbucks = 0
    tellwut = 0
    bing = 0
    schlesinger = 0
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
    for transaction in myBook.transactions:
        if transaction.post_date.year == 2022:
            for spl in transaction.splits:
                if spl.account.fullname == 'Income:Market Research':
                    mrTotal += -spl.value
                    if 'swagbucks' in transaction.description.lower():
                        swagbucks += -spl.value
                    elif 'tellwut' in transaction.description.lower():
                        tellwut += -spl.value
                    elif 'bing' in transaction.description.lower():
                        bing += -spl.value
                    elif 'schlesinger' in transaction.description.lower():
                        schlesinger += -spl.value
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
                if spl.account.fullname == 'Assets:Liquid Assets:Amazon GC':
                    if spl.value > 0:
                        amazonGC += spl.value
                        
    accountedTotal = swagbucks + tellwut + bing + schlesinger + pinecone + paidviewpoint + knowledgePanel + paypal + appen + reckner + check + promo + antidote

    print('     schlesinger: ' + str(schlesinger))                        
    print('           promo: ' + str(promo))
    print('           appen: ' + str(appen))
    print('           misc.: ' + str(mrTotal - accountedTotal))
    print('       swagbucks: ' + str(swagbucks))
    print('   paidviewpoint: ' + str(paidviewpoint))    
    print('  knowledgePanel: ' + str(knowledgePanel))
    print('        antidote: ' + str(antidote))    
    print('         reckner: ' + str(reckner))
    print('            bing: ' + str(bing))
    print('         tellwut: ' + str(tellwut))
    print('        pinecone: ' + str(pinecone))
    print('           check: ' + str(check))
    print('          paypal: ' + str(paypal))    
    print('        MR total: ' + str(mrTotal))
    print('paid in amazonGC: ' + str(amazonGC))

def writeCryptoTransaction():
    mybook = openGnuCashBook('Finance', False, False)
    from_account = 'Assets:Liquid Assets:Sofi:Checking'
    to_account = 'Assets:Non-Liquid Assets:CryptoCurrency:Cardano'
    fee_account = 'Expenses:Bank Fees:Coinbase Fee'
    amount = Decimal(50.00)
    description = 'ADA purchase'
    today = datetime.today()
    year = today.year
    postdate = today.replace(month=1, day=1, year=year)
    with mybook as book:
        split = [Split(value=-amount, memo="scripted", account=mybook.accounts(fullname=from_account)),
                Split(value=round(amount-Decimal(1.99), 2), quantity=round(Decimal(35.052832), 6), memo="scripted", account=mybook.accounts(fullname=to_account)),
                Split(value=round(Decimal(1.99),2), memo="scripted", account=mybook.accounts(fullname=fee_account))]
        Transaction(post_date=postdate.date(), currency=mybook.currencies(mnemonic="USD"), description=description, splits=split)
        book.save()
        book.flush()
        book.close()