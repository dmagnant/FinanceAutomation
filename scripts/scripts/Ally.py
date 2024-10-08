import csv, time, importlib
from datetime import datetime
from decimal import Decimal
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Ally":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange, setDirectory, showMessage)
    from Functions.SpreadsheetFunctions import openSpreadsheet, updateSpreadsheet
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange, showMessage, setDirectory)
    from .Functions.SpreadsheetFunctions import openSpreadsheet, updateSpreadsheet    

def locateAllyWindow(driver):
    found = driver.findWindowByUrl("secure.ally.com")
    if not found:   allyLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    return True

def allyLogin(driver):
    loggedIn = False
    while not loggedIn:
        driver.openNewWindow('https://ally.com/')
        time.sleep(2)
        driver.webDriver.find_element(By.XPATH,"/html/body/header/section[1]/div/nav/ul/li[5]/button").click() # login
        time.sleep(2)
        try:    driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[4]/button").click() # login
        except ElementNotInteractableException:
            driver.webDriver.refresh(); time.sleep(1)
            driver.webDriver.find_element(By.XPATH,"/html/body/header/section[1]/div/nav/ul/li[5]/button").click() # login
            time.sleep(2)
            driver.webDriver.find_element(By.XPATH,"//*[@id='367761b575af35f6ccb5b53e96b2fa2d']/form/div[5]/button").click() # login
        time.sleep(5)
        try: driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div[2]/form/div[3]/button/span").click() # check if login button is still seen
        except NoSuchElementException:  
            try: # check if 2fa is prompted
                driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/main/div/div/div/div/form/div[2]/button/span").click() # Send Security Code
                showMessage('Enter Security Code', 'Enter security code, then click OK on this message')
                driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/main/div/div/div/div/form/button[1]/span").click() # Continue
                try:    driver.find_element(By.XPATH,"/html/body/div[1]/div/main/div/div/div/div/form/div[2]/button/span").click() # Continue
                except  NoSuchElementException: exception = 'device already registered'
            except NoSuchElementException:  exception = 'no 2fa prompted'
        loggedIn = True
    driver.webDriver.find_element(By.PARTIAL_LINK_TEXT, "Joint Checking").click();  time.sleep(5)
    # driver.webDriver.find_element(By.XPATH,'/html/body/div/div[1]/main/div/div/div/div[1]/div/div/span/div[1]/button[1]/span').click()
    # time.sleep(1)
    
def allyLogout(driver):
    locateAllyWindow(driver)
    driver.webDriver.find_element(By.XPATH, "//*[@id='app']/div[1]/header/div[1]/div/nav/div/div[3]/div/button/p").click() # Profile and Settings
    driver.webDriver.find_element(By.XPATH, "//*[@id='profile-menu-logout']/span").click() # Log out

def getAllyBalance(driver):
    locateAllyWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div/div/div[1]/div/section[1]/div/div[1]/div/div[2]/div[1]/span[2]/span/div").text.replace('$', '').replace(',', '')

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
        try:
            date = datetime.strptime(driver.webDriver.find_element(By.XPATH, element + "span").text, '%b %d, %Y').date()
            if date < dateRange['startDate'] or date > dateRange['endDate']:    insideDateRange = False
            else:
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                description = driver.webDriver.find_element(By.XPATH, element + "div/button/span").text
                column += 1
                element = setAllyTransactionElementRoot(row, column)
                amount = driver.webDriver.find_element(By.XPATH, element + "span").text.replace('$', '').replace(',', '')
                if not amount[0].isnumeric():   amount = -Decimal(amount.replace(amount[0], ''))
                transaction = str(date), description, amount
                csv.writer(open(allyActivity, 'a', newline='', encoding="utf-8")).writerow(transaction)
                row += 1
                column = 1
                element = setAllyTransactionElementRoot(row, column)
        except (NoSuchElementException):    insideDateRange = False
    return allyActivity

def importAllyTransactions(driver, account, allyActivity, book, gnuCashTransactions):
    existingTransactions = book.getTransactionsByGnuAccount(account.gnuAccount, transactionsToFilter=gnuCashTransactions)
    for row in csv.reader(open(allyActivity), delimiter=','):
        postDate = datetime.strptime(row[0], '%Y-%m-%d').date()
        rawDescription = row[1]
        amount = Decimal(row[2])
        fromAccount = account.gnuAccount
        if "SAVINGS ACCOUNT XXXXXX9703" in rawDescription.upper():                  description = "Tessa Deposit"
        elif "ALLY BANK TRANSFER" in description.upper():                           description = "Dan Deposit"
        elif "BK OF AMER VISA" in description.upper():                              description = "BoA CC"
        elif "CITY OF MILWAUKE B2P*MILWWA" in description.upper():                  description = "Water Bill"
        elif "COOPER NSM" in description.upper():                                   description = "Mortgage Payment"
        elif 'WE ENERGIES' in description.upper():
            energyBillAmounts = getEnergyBillAmounts(driver, amount, 1)
            description = 'WE ENERGIES PAYMENT'
        else:                                                                       description = rawDescription
        toAccount = book.getGnuAccountName(fromAccount, description=description, row=row)
        if toAccount == 'Expenses:Other':   account.setReviewTransactions(str(postDate) + ", " + description + ", " + str(amount))
        if 'WE ENERGIES' in description.upper(): 
            splits = [{'amount': energyBillAmounts['electricity'], 'account': "Expenses:Utilities:Electricity"},
                      {'amount': energyBillAmounts['gas'], 'account': "Expenses:Utilities:Gas"},
                      {'amount': amount, 'account': account.gnuAccount}
                    ]
        else:
            splits = [{'amount': -amount, 'account':toAccount}, {'amount': amount, 'account':fromAccount}]
        book.writeUniqueTransaction(account, existingTransactions, postDate, description, splits)

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
        except NoSuchElementException:  exception = "caught"
        driver.webDriver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click();  time.sleep(4) # view bill history
    billRow, billColumn, billFound = 2, 7, False
    while not billFound: # find bill based on comparing amount from Arcadia (weBill)
        weBillPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span"
        weBillAmount = driver.webDriver.find_element(By.XPATH, weBillPath).text.replace('$', '')
        if str(abs(amount)) == weBillAmount:    billFound = True
        else:                                   billRow += 1
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gas = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricity = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    return {'electricity': electricity, 'gas': gas, 'total': amount}

def updateEnergyBillAmounts(driver, book, amount):
    driver.openNewWindow('https://www.we-energies.com/secure/auth/l/acct/summary_accounts.aspx')
    today = datetime.today()
    time.sleep(2)
    try:
        # driver.webDriver.find_element(By.XPATH, "//*[@id='signInName']").send_keys(getUsername('WE-Energies (Home)'))
        # driver.webDriver.find_element(By.XPATH, "//*[@id='password']").send_keys(getPassword('WE-Energies (Home)'))
        driver.webDriver.find_element(By.XPATH, "//*[@id='next']").click() # login
        time.sleep(4)
        driver.webDriver.find_element(By.XPATH, "//*[@id='notInterested']/a").click # close out of app notice
    except NoSuchElementException:  exception = "caught"
    driver.webDriver.find_element(By.XPATH, "//*[@id='mainContentCopyInner']/ul/li[2]/a").click() # view bill history
    time.sleep(4)
    billRow, billColumn, billNotFound = 2, 7, True
    while billNotFound:
        weBillAmount = driver.webDriver.find_element(By.XPATH, "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span/span").text.replace('$', '')
        if amount == weBillAmount:  billNotFound = False
        else:   billRow += 1
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    gas = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    billColumn -= 2
    weAmountPath = "/html/body/div[1]/div[1]/form/div[5]/div/div/div/div/div[6]/div[2]/div[2]/div/table/tbody/tr[" + str(billRow) + "]/td[" + str(billColumn) + "]/span"
    electricity = Decimal(driver.webDriver.find_element(By.XPATH, weAmountPath).text.strip('$'))
    splits = []
    splits.append(book.createSplit(electricity, "Expenses:Utilities:Electricity"))
    splits.append(book.createSplit(gas, "Expenses:Utilities:Gas"))
    splits.append(book.createSplit(-round(Decimal(amount),2), book.getGnuAccountName('Ally')))
    book.writeTransaction(today.date().replace(day=24), 'WE ENERGIES PAYMENT', splits)
    print(f'posted transaction: \n' f'date: {str(today.date())} \n' f'total: {str(amount)} \n' f'electricity: {str(electricity)}\n' f'gas: {str(gas)}')
    # book.writeUtilityTransaction({'electricity': electricity, 'gas': gas, 'total': amount})
    # splits=[Split(value=transactionInfo['electricity'], account=self.getGnuAccount("Expenses:Utilities:Electricity")),
    #     Split(value=transactionInfo['gas'], account=self.getGnuAccount("Expenses:Utilities:Gas")),
    #     Split(value=-round(Decimal(transactionInfo['total']), 2), account=self.getGnuAccount("Assets:Ally Checking Account"))]
    # Transaction(post_date=today.date().replace(day=24), currency=book.currencies(mnemonic="USD"), description='WE ENERGIES PAYMENT', splits=splits)
    updateSpreadsheet('Home', str(today.year) + ' Balance', 'Energy Bill', today.month, -float(amount))
    openSpreadsheet(driver, 'Home', str(today.year) + ' Balance')
    driver.findWindowByUrl("/scripts/ally")

def runAlly(driver, account, book, gnuCashTransactions, dateRange):
    locateAllyWindow(driver)
    account.setBalance(getAllyBalance(driver))
    allyActivity = captureAllyTransactions(driver, dateRange)
    importAllyTransactions(driver, account, allyActivity, book, gnuCashTransactions)
    account.updateGnuBalance(book.getGnuAccountBalance(account.gnuAccount))

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Home')
    Ally = USD("Ally", book)
    dateRange = getStartAndEndOfDateRange(timeSpan=7)
    gnuCashTransactions = book.getTransactionsByDateRange(dateRange)
    runAlly(driver, Ally, book, gnuCashTransactions, dateRange)
    Ally.getData()
    # allyLogout(driver)
    book.closeBook()
