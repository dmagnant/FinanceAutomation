import random, time, pyautogui, pygetwindow
from random_word import RandomWords
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        NoSuchWindowException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "InboxDollars":
    from Classes.WebDriver import Driver
    from Classes.Asset import USD
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, setDirectory, getLogger
else:
    from .Classes.Asset import USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, setDirectory, getLogger

def inboxDollarsLogin(driver):
    driver.openNewWindow("https://www.inboxdollars.com")

def locateInboxDollarsWindow(driver):
    found = driver.findWindowByUrl("inboxdollars.com")
    if not found:   inboxDollarsLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    closeInboxDollarsPopUps(driver)

def closeInboxDollarsPopUps(driver):
    driver.getElementAndClick('xpath', "/html/body/div[3]/reset-styles/div[1]/div[1]/aside/div/button[1]", wait=0.2) # X
    driver.getElementAndClick('id', 'lightboxExit', wait=0.2) # to exit pop-up    

def inboxDollarsContentDiscovery(driver):
    driver.openNewWindow("https://www.inboxdollars.com/discover-new/explore")
    contentDiscoverWindow = driver.webDriver.current_window_handle
    windowCount = driver.getWindowCount()
    cycleThroughInboxDollarsOffers(driver, "/html/body/div[2]/div[2]/div[2]/div[2]/main/div[3]/div[2]/div[2]/div/div/ul/li[cardNum]", contentDiscoverWindow, windowCount) # featured offers
    cycleThroughInboxDollarsOffers(driver, "/html/body/div[2]/div[2]/div[2]/div[2]/main/div[3]/section[2]/ul/li[cardNum]", contentDiscoverWindow, windowCount) # explore web content and earn
    driver.closeWindowsExcept([':8000/'])

def cycleThroughInboxDollarsOffers(driver, offerPath, contentDiscoverWindow, windowCount):
    cardNum = 1
    while True:
        modifiedOfferPath = offerPath.replace('cardNum', str(cardNum))
        offer = driver.getElement('xpath', modifiedOfferPath, wait=0.5) # click to open
        if not offer: 
            print("failed to find offer element")
            return False
        reviewInboxDollarsOffer(driver, offer, contentDiscoverWindow, windowCount)
        cardNum += 1

def reviewInboxDollarsOffer(driver, offer, contentDiscoverWindow, windowCount):
    if "$0.01" in offer.text.lower():
        offer.click()
        driver.getElementAndClick('xpath', "/html/body/div[3]/reset-styles/div[1]/div/aside/div/div[2]/button", wait=0.5) # Earn SB
        time.sleep(1)
        newWindowCount = driver.getWindowCount()
        if newWindowCount > windowCount:
            driver.webDriver.switch_to.window(contentDiscoverWindow)
        driver.getElementAndClick('xpath', "/html/body/div[3]/reset-styles/div[1]/div/aside/div/button", wait=0.5) # X to close      
        
def inboxDollarsToDoList(driver):
    closeInboxDollarsPopUps(driver)
    list_item_num, button_num, button_not_clicked, main = 1, 2, True, driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1]
    while list_item_num <= 8:
        if not driver.getElement('xpath', "/html/body/div[2]/div[2]/div[1]/header/div[1]/div[1]/div[4]/div[2]/div[2]/div/div[1]", wait=2): # look for Daily List Header
            driver.getElementAndClick('xpath', "/html/body/div[2]/div[2]/div[1]/header/div[1]/div[1]/div[4]/div[2]/div[2]/button/span/div/span[1]", wait=2) # click to show To Do List
        time.sleep(3)
        list_item = driver.getElement('xpath', "/html/body/div[2]/div[2]/div[1]/header/div[1]/div[1]/div[4]/div[2]/div[2]/div/div[3]/div/div[" + str(list_item_num) + "]", wait=2)
        if list_item.text == "Add A Magic Receipts Deal":
            list_item.click()
            time.sleep(4)
            while button_not_clicked:
                button = driver.getElement('xpath', "/html/body/div[2]/div[2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/div[4]/ul/li[" + str(button_num) +"]/div/a/div[2]/button/span", wait=2)
                if not button:
                    button = driver.getElement('xpath', "/html/body/div[2]/div[2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/div[4]/ul/li[" + str(button_num) +"]/div/a/div[3]/button/span", wait=2, allowFail=False)
                    if not button:
                        print("FAILED TO ADD MAGIC DEAL")
                        break
                if button.text == 'Add to List':    
                    button.click(); 
                    button_not_clicked = False
                else:                               
                    button_num+=1
            driver.webDriver.get('https://www.inboxdollars.com/'); time.sleep(2)
        elif list_item.text == 'Daily Games':
            driver.webDriver.get("https://www.inboxdollars.com/games/gianthamsterrun")
            time.sleep(20)
            pyautogui.leftClick(780, 775)
            num = 1
            while num < 15:
                pyautogui.press('up')
                time.sleep(2)
                num += 1
            driver.webDriver.get('https://www.inboxdollars.com/'); time.sleep(2)
            print("Daily Games attempted")
        elif list_item.text == "Deal of the Day" or list_item.text == "Daily Activity":
            window_num_before = len(driver.webDriver.window_handles)
            print("Clicking on " + list_item.text)
            driver.getElementAndClick('link_text', list_item.text, wait=0.1)
            # list_item.click() # possible replaced with the above line
            window_num_after = len(driver.webDriver.window_handles)
            if window_num_before == window_num_after:   driver.webDriver.get('https://www.inboxdollars.com/')
            else:
                driver.switchToLastWindow()
                driver.webDriver.close()
                driver.webDriver.switch_to.window(main)
        list_item_num += 1          
    return True

def learnAndEarn(driver):
    closeInboxDollarsPopUps(driver)
    answered = False
    driver.webDriver.get('https://www.inboxdollars.com/learn-and-earn');    time.sleep(1)
    if driver.getElementAndClick('id', "a1", wait=2): # try first answer
        if driver.getElementAndClick('id', "poll-submit", wait=2):
            answered = True # vote & earn
    driver.webDriver.get('https://www.inboxdollars.com/home');    time.sleep(1)
    return answered

def getInboxDollarsBalance(driver):
    locateInboxDollarsWindow(driver)
    rawBalance = driver.getElementText('xpath', "/html/body/div[2]/div[2]/div[1]/header/div[1]/div[1]/div[4]/div[1]/a[1]", wait=2, allowFail=False)
    if rawBalance:
        return rawBalance.replace('$', '').replace(',', '')
    
def claimInboxDollarsRewards(driver, account):
    if float(account.balance) < 10030:
        print('Not enough InboxDollars to redeem')
        return False
    locateInboxDollarsWindow(driver)
    driver.webDriver.get("https://www.inboxdollars.com/p/prize/34668/PayPal-100")
    # time.sleep(4)
    driver.getElementAndClick('id', "redeemBtnHolder") # Claim Reward
    driver.getElementAndClick('id', "redeemBtn") # Claim a Gift Card
    driver.getElementAndClick('id', "confirmOrderCta") # Confirm (order details)
    driver.getElementAndSendKeys('id', "securityQuestionInput", 'Tiger')
    driver.getElementAndClick('id', "verifyViaSecurityQuestionCta") # click Submit

def runInboxDollars(driver, account, book, log=getLogger()):
    locateInboxDollarsWindow(driver)
    learnEarn = learnAndEarn(driver)
    log.info(f'Learn and Earn completed: {learnEarn}')
    toDoList = inboxDollarsToDoList(driver)
    log.info(f'To Do List completed: {toDoList}')
    inboxDollarsContentDiscovery(driver)
    account.setBalance(getInboxDollarsBalance(driver))
    book.updateMRBalance(account)
    claimInboxDollarsRewards(driver, account)
    return True

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    InboxDollars = USD("InboxDollars", book)
    locateInboxDollarsWindow(driver)
    # runInboxDollars(driver, InboxDollars, book)
    book.closeBook()
