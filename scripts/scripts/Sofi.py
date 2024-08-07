import csv, time, pyautogui
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Sofi":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Fidelity import getFidelityTransferAccount
    from Functions.GeneralFunctions import (getPassword,
                                            getStartAndEndOfDateRange,
                                            getUsername, setDirectory,
                                            showMessage, modifyTransactionDescription)
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Fidelity import getFidelityTransferAccount
    from .Functions.GeneralFunctions import (getPassword,
                                             getStartAndEndOfDateRange,
                                             setDirectory, showMessage, modifyTransactionDescription)
def locateSofiWindow(driver):
    found = driver.findWindowByUrl("sofi.com")
    if not found:   sofiLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    return True

def checkIfLoggedIn(driver):
    return driver.webDriver.current_url == "https://www.sofi.com/member-home"
    
def sofiLogin(driver):
    notLoggedIn = True
    while notLoggedIn:
        driver.openNewWindow('https://www.sofi.com/login')
        time.sleep(2)
        try:
            driver.webDriver.find_element(By.XPATH, "//*[@id='widget_block']/div/div[2]/div/div/main/section/div/div/div/form/div[2]/button").click() # login
            notLoggedIn = checkIfLoggedIn(driver)
        except NoSuchElementException:
            try:
                pyautogui.press('tab')
                pyautogui.press('space')
                time.sleep(5)
            except NoSuchElementException:
                notLoggedIn = checkIfLoggedIn(driver)
        # driver.webDriver.find_element(By.ID,"error-3") # look for email is required error
        # driver.webDriver.find_element(By.ID, "username").send_keys(getUsername('Sofi'))
        # time.sleep(1)
        # driver.webDriver.find_element(By.ID, "password").send_keys(getPassword('Sofi'))
        # time.sleep(1)
        # driver.webDriver.find_element(By.XPATH, "//*[@id='widget_block']/main/section/div/div/div/form/div[2]/button").click() # login
        # try:
        #     driver.webDriver.find_element(By.ID,'code')
        #     showMessage("OTP Verification", "Enter code from phone, then click OK")
        #     driver.webDriver.find_element(By.XPATH,"//*[@id='mainContent']/div/div/div[2]/div[3]/div[1]/label/span").click() # remember device
        #     driver.webDriver.find_element(By.ID,"verifyCode").click()
        # except NoSuchElementException:  exception = 'otp not required'

def sofiLogout(driver):
    locateSofiWindow(driver)
    driver.webDriver.get("https://www.sofi.com/member-home")
    driver.webDriver.find_element(By.XPATH, "//*[@id='root']/header/nav/div[3]/div[2]/button").click() # Name on top right
    driver.webDriver.find_element(By.XPATH, "//*[@id='user-dropdown']/div/div/a[4]").click() # log out

def setMonthlySpendTarget(driver):
    locateSofiWindow(driver)
    baseWindow = driver.webDriver.current_window_handle
    driver.openNewWindow('https://www.sofi.com/relay/app/spending/monthly-spending')
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH,"//*[@id='mainContent']/section/section[1]/div/h3/button").click() # Edit
    time.sleep(1)
    driver.webDriver.find_element(By.XPATH,"//*[@id='mainContent']/section/form/div[3]/div/div[2]/button[2]").click() # Save
    driver.webDriver.close()
    driver.webDriver.switch_to.window(baseWindow)


def getSofiBalanceAndOrientPage(driver, account):
    locateSofiWindow(driver)
    driver.webDriver.get("https://www.sofi.com/my/money/account/1000028154579/account-detail") if 'checking' in account.name.lower() else driver.webDriver.get("https://www.sofi.com/my/money/account/1000028154560/account-detail")
    time.sleep(2)
    table = 1
    div = '2' if 'checking' in account.name.lower() else '4'
    def findBalanceElement(webDriver, table, div):
        return webDriver.find_element(By.XPATH, "/html/body/div[1]/main/div[3]/div[" + div + "]/table[" + str(table)  + "]/tbody/tr[1]/td[6]/span").text.strip('$').replace(',', '')
    balance = findBalanceElement(driver.webDriver, table, div)
    if balance == "": # Pending transactions will load as table 1 with a blank balance. if pending transactions exist, move to next Table
        table += 1
        balance = findBalanceElement(driver.webDriver, table, div)
    account.setBalance(balance)
    return {'table': table,'div': div}

def setSofiTransactionElementRoot(table, row, column, div): return "/html/body/div/main/div[3]/div[" + div + "]/table[" + str(table) + "]/tbody/tr[" + str(row) + "]/td[" + str(column) + "]/span"

def getTransactionsFromSofiWebsite(driver, dateRange, today, tableStart, div):
    sofiActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\sofi.csv";     open(sofiActivity, 'w', newline='').truncate()
    year, table, insideDateRange, previousMonth, row, column = today.year, tableStart, True, False, 1, 1
    elementRoot = setSofiTransactionElementRoot(table, row, column, div)
    while insideDateRange:
        try:
            date = driver.webDriver.find_element(By.XPATH, elementRoot).text
            if "/" not in date:
                month = datetime.strptime(date[:3], "%b").month
                day = date[4:]
                date = f'{str(month)}/{day}/{str(year-2000)}'
            sofiDate = datetime.strptime(date, "%m/%d/%y").date()
            if sofiDate < dateRange['startDate'] or sofiDate > dateRange['endDate']:    insideDateRange = False
            else:
                column += 1
                description = driver.webDriver.find_element(By.XPATH, setSofiTransactionElementRoot(table, row, column, div)).text
                column += 3
                amount = driver.webDriver.find_element(By.XPATH, setSofiTransactionElementRoot(table, row, column, div)).text.replace('$', '').replace(',', '')
                description = modifyTransactionDescription(description, amount)
                if description == "Fidelity Transfer":
                    account = getFidelityTransferAccount(driver, amount.replace('-',''), sofiDate)
                    description = description + " " + account
                    locateSofiWindow(driver)
                transaction = sofiDate, description, amount
                csv.writer(open(sofiActivity, 'a', newline='')).writerow(transaction)
                row += 1
                column = 1
                elementRoot = setSofiTransactionElementRoot(table, row, column, div)
        except NoSuchElementException:
            if not previousMonth:
                table += 1
                row = 1
                column = 1
                elementRoot = setSofiTransactionElementRoot(table, row, column, div)
                previousMonth = True
            else:   insideDateRange = False
    return sofiActivity

def runSofiAccount(driver, dateRange, today, account, book):
    page = getSofiBalanceAndOrientPage(driver, account)
    sofiActivity = getTransactionsFromSofiWebsite(driver, dateRange, today, page['table'], page['div'])
    book.importUniqueTransactionsToGnuCash(account, sofiActivity, driver, dateRange, 0)

def runSofi(driver, accounts, book):
    today = datetime.today().date()
    dateRange = getStartAndEndOfDateRange(today, 7)
    locateSofiWindow(driver)
    for account in accounts:
        runSofiAccount(driver, dateRange, today, account, book)
        account.updateGnuBalance(book.getBalance(account.gnuAccount))
    if today.day <= 7:          setMonthlySpendTarget(driver)  
    driver.webDriver.get("https://www.sofi.com/my/money/account/#/1000028154579/account-detail") # switch back to checking page

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Checking = USD("Sofi Checking", book)
    Savings = USD("Sofi Savings", book)
    accounts = [Checking, Savings]
    runSofi(driver, accounts, book)
    for account in accounts:
        account.getData()
    book.closeBook()
    
# if __name__ == '__main__':
#     book = GnuCash('Finance')
#     driver = Driver("Chrome")
#     today = datetime.today().date()
#     dateRange = getStartAndEndOfDateRange(today, 7)
#     Savings = USD("Sofi Savings", book)
#     sofiActivity = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\sofi.csv"
#     book.importUniqueTransactionsToGnuCash(Savings, sofiActivity, driver, dateRange, 0)
