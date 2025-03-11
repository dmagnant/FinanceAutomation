import time, pyautogui
from datetime import datetime
from decimal import Decimal

if __name__ == '__main__' or __name__ == "Paypal":
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Classes.Asset import USD    
    from Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange
else:   
    from .Functions.GeneralFunctions import getPassword, getStartAndEndOfDateRange
    from .Classes.GnuCash import GnuCash
    from .Classes.Asset import USD

def locatePayPalWindow(driver):
    found = driver.findWindowByUrl("paypal.com/myaccount")
    if not found:   payPalLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def payPalLogin(driver):
    driver.openNewWindow('https://www.paypal.com/us/signin')
    time.sleep(3)
    driver.getElementAndClick('id', 'btnLogin', wait=2) # click login as pass/user is pre-filled (for now)
    # num = 1
    # while num <3:
    #     # driver.getElementAndSendKeys('id', 'password', getPassword('Paypal'))
    #     if driver.getElementAndClick('id', 'btnLogin', wait=2):
    #         time.sleep(2)
    #         if driver.find_element('xpath', "//*[@id='content']/h1", wait=2):
    #             pyautogui.moveTo(825,400)
    #             pyautogui.leftClick(825,400)
    #             time.sleep(5)
    #     if not driver.getElement('id', 'password'):
    #         break
    #     num+=1

def transferMoney(driver):
    rawBalance = driver.getElementText('xpath', "//*[@id='reactContainer__balance']/div/div/div[1]")

    if Decimal(rawBalance.replace('$','').replace(' USD', '')) > 0:
        driver.getElementAndClick('xpath', "//*[@id='reactContainer__balance']/div/div/a") # transfer money
        # time.sleep(2)
        driver.getElementAndClick('xpath', "//*[@id='mainModal']/div/div/div/div/div/div[1]/ul/li[1]/a/span/p[2]") # transfer to bank
        # time.sleep(1)
        bank = driver.getElementText('xpath', "//*[@id='mainModal']/div/div/div/div/form/div/div/div/div[1]/span/span[2]/span[1]")
        if "savings" in bank.lower():   
            driver.getElementAndClick('xpath', "//*[@id='mainModal']/div/div/div/div/form/div/div/div/button")

def checkUncategorizedPaypalTransactions(driver, book, Paypal, dateRange):
    transactions = [tr for tr in book.readBook.transactions
        if tr.post_date < dateRange['startDate']
        for spl in tr.splits
        if spl.account.fullname == Paypal.gnuAccount]
    for tr in transactions:
        Paypal.setReviewTransactions(str(tr.post_date) + ", " + tr.description + ", " + str(tr.splits[0].value))
    if Paypal.reviewTransactions:
        locatePayPalWindow(driver)
    
def runPaypal(driver):
    locatePayPalWindow(driver)
    transferMoney(driver)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    runPaypal(driver)
    
    
    # book = GnuCash('Finance')
    # today = datetime.today().date()
    # dateRange = getStartAndEndOfDateRange(today, 7)
    # Paypal = USD("Paypal", book)
    # checkUncategorizedPaypalTransactions(book, Paypal, dateRange)