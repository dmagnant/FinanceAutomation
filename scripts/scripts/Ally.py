import csv, time, json, os
from datetime import datetime
from decimal import Decimal
from selenium.webdriver.common.keys import Keys


if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Classes.Spreadsheet import Spreadsheet
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange, setDirectory, showMessage, getUsername, getNotes)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Classes.Spreadsheet import Spreadsheet

    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange, showMessage, setDirectory, getUsername, getNotes)

def locateAllyWindow(driver):
    found = driver.findWindowByUrl("secure.ally.com")
    if not found:   allyLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    return True

def allyLogin(driver):
    loggedIn = False
    while not loggedIn:
        driver.openNewWindow('https://ally.com/')
        # time.sleep(2)
        driver.getElementAndClick('xpath', "html/body/header/section[1]/div/nav/ul/li[5]/button") # login
        # time.sleep(2)
        if not driver.getElementAndClick('xpath', "//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[4]/button", wait=2): # login
            driver.webDriver.refresh(); time.sleep(1)
            driver.getElementAndClick('xpath', "html/body/header/section[1]/div/nav/ul/li[5]/button") # login
            # time.sleep(2)
            driver.getElementAndClick('xpath', "//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button") # login
        time.sleep(5)
        if not driver.getElementAndClick('xpath', 'html/bmody/div[1]/main/div/div/div/div/div[2]/form/div[3]/button/span', wait=2): # login 
            if driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/div/div/div/div/form/div[2]/button/span", wait=2): # Send Security Code
                showMessage('Enter Security Code', 'Enter security code, then click OK on this message')
                driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/div/div/div/div/form/button[1]/span") # Continue
                driver.getElementAndClick('xpath', "/html/body/div[1]/div/main/div/div/div/div/form/div[2]/button/span") # Continue
        loggedIn = True
    driver.getElementAndClick('partial_link_text', 'Joint Checking');  time.sleep(5)
    
def allyLogout(driver):
    locateAllyWindow(driver)
    driver.getElementAndClick('xpath', "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p") # Profile and Settings
    driver.getElementAndClick('xpath', "//*[@id='profile-menu-logout']/span") # Log out

def getAllyBalance(driver):
    locateAllyWindow(driver)
    balance = driver.getElementText('xpath', "/html/body/div/div[1]/main/div/div/div/div[1]/div/section[1]/div/div[1]/div/div[2]/div[1]/span[2]/span/div")
    return balance.replace('$', '').replace(',', '') if balance else False

def captureAllyTransactions(driver, dateRange):
    def setAllyTransactionElementRoot(row, column):
        return "/html/body/div[1]/div[1]/main/div/div/div/div[1]/div/div/div[2]/section[2]/div[2]/div/table/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/div/"

    allyActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\ally.csv"
    open(allyActivity, 'w', newline='').truncate()
    row = column = 1
    element = setAllyTransactionElementRoot(row, column)
    time.sleep(6)
    insideDateRange = True
    while insideDateRange:
        rawDate = driver.getElementText('xpath', element + "span")
        if not rawDate: 
            break
        date = datetime.strptime(rawDate, '%b %d, %Y').date()
        if date < dateRange['startDate'] or date > dateRange['endDate']:    insideDateRange = False
        else:
            column += 1
            element = setAllyTransactionElementRoot(row, column)
            description = driver.getElementText('xpath', element + "div/button/span")
            column += 1
            element = setAllyTransactionElementRoot(row, column)
            amount = driver.getElementText('xpath', element + "span").replace('$', '').replace(',', '')
            if not amount[0].isnumeric():   amount = -Decimal(amount.replace(amount[0], ''))
            transaction = str(date), description, amount
            csv.writer(open(allyActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
            row += 1
            column = 1
            element = setAllyTransactionElementRoot(row, column)
    return allyActivity

def payWaterBill(driver, book):
    def getWaterFeeElement(tr, td):
        return f"//*[@id='tblAccountInfo']/tbody/tr[{str(tr)}]/td[{str(td)}]"
    
    driver.findWindowByUrl('bill2pay.com')
    today = datetime.today()
    Home = Spreadsheet('Home', str(today.year) + ' Balance', driver)
    paymentAccountDetails = json.loads(getNotes('Ally Bank'))
    today = datetime.today()
    driver.openNewWindow('https://paywater.milwaukee.gov/webclient/user/login.seam')
    if driver.getElementAndSendKeys('id', 'account', getUsername('Water'), wait=2):
        driver.getElementAndClick('xpath', "//*[@id='anonymous-form']/div[2]/button") # login
    billAmount = driver.getElementText('id', "dashboardMyAccountsShowBalances").replace('$','')
    driver.getElementAndClick('id', 'payBill_btn')
    time.sleep(1)
    driver.webDriver.get(f'https://paywater.milwaukee.gov/app/PaymentGateway?ccpa={billAmount}')
    driver.getElementAndSendKeys('id', 'txtUserField1', os.environ.get('firstName') + " " + os.environ.get('lastName'))
    driver.getElementAndSendKeys('id', 'txtPhone', os.environ.get('Phone'))
    driver.getElementAndClick('id', 'btnSubmit') # Continue
    driver.getElementAndSendKeys('id', 'txtNameonBankAccount', os.environ.get('firstName') + " " + os.environ.get('lastName'))
    driver.getElementAndSendKeys('id', 'ddlBankAccountType', Keys.DOWN)
    driver.getElementAndSendKeys('id', 'txtBankRoutingNumber', paymentAccountDetails['routing'])
    driver.getElementAndSendKeys('id', 'txtBankAccountNumber', paymentAccountDetails['account'])
    driver.getElementAndSendKeys('id', 'txtBankAccountNumber2', paymentAccountDetails['account'])
    driver.getElementAndClick('id', 'btnSubmitAch') # Continue
    billTotal = driver.getElementText('xpath', "//*[@id='tblAccountInfo']/tbody/tr[7]/td[2]").replace('$','')
    driver.getElementAndSendKeys('id', 'txtEmailAddress', os.environ.get('Email'))
    time.sleep(2)
    driver.getElementAndClick('id', 'chkTermsAgree') # agree to T&C
    time.sleep(2)
    driver.getElementAndClick('id', 'btnSubmit') # Make a Payment
    totalIncludingFee = driver.getElementText('xpath', "//*[@id='tblAccountInfo']/tbody/tr[10]/td[2]").replace('$','')
    splits = [book.createSplit(round(Decimal(totalIncludingFee)), 2), book.getGnuAccountFullName('Water'), book.createSplit(-round(Decimal(totalIncludingFee), 2), book.getGnuAccountFullName('Ally'))]
    book.writeTransaction(today.date(), 'Water Bill', splits)
    Home.updateSpreadsheet('Water Bill', today.month, -float(totalIncludingFee))
    driver.findWindowByUrl("/scripts/ally")

def importAllyTransactions(driver, account, allyActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(allyActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1]
        amount = Decimal(row[2])
        fromAccount = account.gnuAccount
        description = rawDescription
        toAccount = book.getGnuAccountFullName('Other')
        if "SAVINGS ACCOUNT XXXXXX9703" in rawDescription.upper():                  
            description = "Tessa Deposit"
            toAccount = book.getGnuAccountFullName("Tessa's Contributions")
        elif "ALLY BANK TRANSFER" in rawDescription.upper():                           
            description = "Dan Deposit"
            toAccount = book.getGnuAccountFullName("Dan's Contributions")
        elif "BK OF AMER VISA" in rawDescription.upper():                              
            description = "BoA CC"
            toAccount = book.getGnuAccountFullName("BoA-joint")
        elif "CITY OF MILWAUKE B2P*MILWWA" in rawDescription.upper():                  
            description = "Water Bill"
            toAccount = book.getGnuAccountFullName("Water")
        elif "COOPER NSM" in rawDescription.upper():                                   
            description = "Mortgage Payment"
            toAccount = book.getGnuAccountFullName("Liabilities") + ":Mortgage Loan"
        elif 'WE ENERGIES' in rawDescription.upper():
            energyBillAmounts = getEnergyBillAmounts(driver, amount, 1)
            description = 'WE ENERGIES PAYMENT'
        # toAccount = book.getGnuAccountFullName(fromAccount, description=description, row=row)
        if toAccount == 'Expenses:Other':   account.setReviewTransactions(str(postDate) + ", " + description + ", " + str(amount))
        if 'WE ENERGIES' in description.upper(): 
            splits = [{'amount': energyBillAmounts['electricity'], 'account': book.getGnuAccountFullName("Electricity")},
                      {'amount': energyBillAmounts['gas'], 'account': book.getGnuAccountFullName("Gas")},
                      {'amount': amount, 'account': account.gnuAccount}
                    ]
        else:
            splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

def getEnergyBillAmounts(driver, amount, energyBillNum):
    if energyBillNum == 1:
        driver.openNewWindow('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx')
        time.sleep(2)
        if driver.getElementAndSendKeys('id', 'signInName', getUsername('WE-Energies (Home)'), wait=2):
            driver.getElementAndSendKeys('id', 'password', getPassword('WE-Energies (Home)'))
            driver.getElementAndClick('xpath', "//*[@id='next']") # login
            time.sleep(4)
            driver.getElementAndClick('xpath', "//*[@id='notInterested']/a") # close out of app notice
        driver.getElementAndClick('xpath', "//*[@id='mainContentCopyInner']/ul/li[2]/a") # view bill history
        time.sleep(4)
    billRow, billColumn, billFound = 2, 7, False
    while not billFound: # find bill based on comparing amount from Arcadia (weBill)
        weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
        weBillAmount = driver.getElementText('xpath', weBillPath).replace('$', '')
        if str(abs(amount)) == weBillAmount:    billFound = True
        else:                                   billRow += 1
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gas = Decimal(driver.getElementText('xpath', weAmountPath).strip('$'))
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricity = Decimal(driver.getElementText('xpath', weAmountPath).strip('$'))
    return {'electricity': electricity, 'gas': gas, 'total': amount}

def updateEnergyBillAmounts(driver, book, amount):
    today = datetime.today().date()
    Home = Spreadsheet('Home', str(today.year) + ' Balance', driver)
    driver.openNewWindow('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx')    
    time.sleep(2)
    if driver.getElementAndClick('id', 'signInName', wait=2):
        driver.getElementAndClick('xpath', "//*[@id='next']", wait=3) # login
        driver.getElementAndClick('xpath', "//*[@id='notInterested']/a", wait=2) # close out of app notice
    driver.getElementAndClick('xpath', "//*[@id='mainContentCopyInner']/ul/li[2]/a", allowFail=False) # view bill history
    time.sleep(4)
    billRow, billColumn, billNotFound = 2, 7, True
    while billNotFound:
        weBillAmount = driver.getElementText('xpath', "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span").replace('$', '')
        if amount == weBillAmount:  billNotFound = False
        else:   billRow += 1
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gas = Decimal(driver.getElementText('xpath', weAmountPath).strip('$'))
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricity = Decimal(driver.getElementText('xpath', weAmountPath).strip('$'))
    splits = []
    splits.append(book.createSplit(electricity, "Expenses:Utilities:Electricity"))
    splits.append(book.createSplit(gas, "Expenses:Utilities:Gas"))
    splits.append(book.createSplit(-round(Decimal(amount),2), book.getGnuAccountFullName('Ally')))
    book.writeTransaction(today.replace(day=24), 'WE ENERGIES PAYMENT', splits)
    print(f'posted transaction: \n' f'date: {str(today)} \n' f'total: {str(amount)} \n' f'electricity: {str(electricity)}\n' f'gas: {str(gas)}')
    Home.updateSpreadsheet('Energy Bill', today.month, -float(amount))
    driver.findWindowByUrl("/scripts/ally")

def mortgageBill(driver, book):
    today = datetime.today()
    total = round(Decimal(2000.00),2)
    Home = Spreadsheet('Home', str(today.year) + ' Balance', driver)
    Mortgage = Spreadsheet('Mortgage', 'Mortgage', driver)
    row = Mortgage.firstRowOfThisYear
    while True:
        paymentDate = datetime.strptime(Mortgage.readCell(Mortgage.dateColumn+str(row)), '%m/%d/%Y').date()
        if paymentDate.month == today.month and paymentDate.year == today.year:
            interest = round(Decimal(Mortgage.readCell(Mortgage.interestColumn+str(row))),2)
            break
        else:   row+=1
    # write transaction # 
    splits = []
    splits.append(book.createSplit(interest, "Expenses:Home Expenses:Mortgage Interest"))
    splits.append(book.createSplit(total - interest, "Liabilities:Mortgage Loan"))
    splits.append(book.createSplit(-total, book.getGnuAccountFullName('Ally')))
    book.writeTransaction(today.date(), 'Mortgage Payment', splits)
    # update Home spreadsheet # 
    Home.updateSpreadsheet('Mortgage', today.month, -float(total))
    driver.findWindowByUrl("/scripts/ally")

def runAlly(driver, account, book, gnuCashTransactions, dateRange):
    locateAllyWindow(driver)
    account.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver, dateRange)
    importAllyTransactions(driver, account, allyActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))

# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Home')
#     Ally = USD("Ally", book)
#     dateRange = getStartAndEndOfDateRange(timeSpan=7)
#     gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
#     runAlly(driver, Ally, book, gnuCashTransactions, dateRange)
#     Ally.getData()
#     # allyLogout(driver)
#     book.closeBook()
    
# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Home')
#     driver.findWindowByUrl("paywater.milwaukee.gov")
#     # billAmount = driver.getElementText('id', "paymentAmountValue")
#     # print(billAmount)
#     import os, shutil, time, zipfile, sys
#     from selenium import webdriver
#     from selenium.webdriver.common.keys import Keys
#     from selenium.common.exceptions import (InvalidArgumentException,
#                                             WebDriverException, TimeoutException)
#     from selenium.webdriver.chrome.service import Service
#     from selenium.webdriver.common.by import By
#     from selenium.webdriver.support.wait import WebDriverWait
#     from selenium.webdriver.support import expected_conditions as EC
    # try:
    #     element = WebDriverWait(driver.webDriver, 5).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='billTable']/tbody/tr[1]/td[3]/div")))
    #     print(element.text)
    # except TimeoutException:
    #     print('FALSE')

if __name__ == '__main__':
    driver = Driver("Chrome")
    # Mortgage = Spreadsheet('Mortgage', 'Mortgage', driver)
    # row = Mortgage.firstRowOfThisYear
    # print(row)
    def getWaterFeeElement(tr, td):
        return f"//*[@id='tblAccountInfo']/tbody/tr[{str(tr)}]/td[{str(td)}]"
    driver.findWindowByUrl('bill2pay.com')
    tr = 3
    td = 1
    while True:
        text = driver.getElementText('xpath', getWaterFeeElement(tr, td))
        print(text)
        if text == 'CONVENIENCE FEE':
            td += 1
            fee = driver.getElementText('xpath', getWaterFeeElement(tr, td))
            print(fee)
            break
        tr+=1



    


