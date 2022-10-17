
import time
from datetime import datetime
from decimal import Decimal

from .GeneralFunctions import closeExpressVPN, getPassword, getUsername, showMessage
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


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
    elif "BARCLAYCARD US" in description.upper():
        description = "Barclays CC"
    elif "BARCLAYCARD US ACH REWARD" in description.upper():
        description = "Barclays CC Rewards"
    elif "BK OF AMER VISA" in description.upper():
        description = "BoA CC"
    elif "CASH REWARDS STATEMENT CREDIT" in description.upper():
        description = "BoA CC Rewards"
    return description

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
        toAccount = "Assets:Liquid Assets:Promos:alliant"        
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

def getEnergyBillAmounts(driver, directory, amount, energyBillNum):
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
