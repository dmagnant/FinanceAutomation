import random, time, pyautogui, pygetwindow
from random_word import RandomWords
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        NoSuchWindowException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Swagbucks":
    from Classes.WebDriver import Driver
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, setDirectory, getLogger
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, setDirectory, getLogger

def getSwagbucksBasePath(): return '/html/body/div[2]/div[' 
    
def closePopUps(driver):
    driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/section/section/aside/button[2]", wait=1)  # Yay for me
    driver.getElementAndClick('id', 'lightboxExit', wait=1) # to exit pop-up

def locateSwagBucksWindow(driver):
    found = driver.findWindowByUrl("swagbucks.com")
    if not found:   swagBucksLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def swagBucksLogin(driver):
    driver.openNewWindow('https://www.swagbucks.com/')
    closePopUps(driver)
        
def swagBuckscontentDiscovery(driver):
    driver.openNewWindow("https://www.swagbucks.com/discover/alloffers?sort=2")
    cardNum = 1
    closePopUps(driver)
    while True:
        contentPath = getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[2]/div[1]/section[" + str(cardNum) + "]"
        earnings = driver.getElementText('xpath', contentPath + "/p/span/span[3]", wait=2)
        if not earnings:
            cardNum += 1; 
            continue
        description = driver.getElementText('xpath', contentPath + "/button", wait=2, allowFail=False)
        if not description:
            if cardNum == 1:    showMessage('failed to find content discovery', 'check script for correct element')
            else:       break
        if "1 sb" in earnings.lower() or "check out the latest deals" == description.lower():
            clickAmt = 1
            while clickAmt < 5:
                driver.getElementAndClick('xpath', contentPath)
                driver.getElementAndClick('xpath', "/html/body/aside[2]/div/div[1]/div[2]/div[2]/div/div[2]/a") # get SB
                # time.sleep(1)
                driver.getElementAndClick('xpath', "/html/body/aside[2]/div/button") # X to close
                clickAmt += 1
                if "discover daily interests" != description.lower():
                    break
        elif "sb per" in earnings.lower() or int(earnings.lower().replace(" sb", '')) > 4:  break
        cardNum += 1
    driver.closeWindowsExcept([':8000/'])

def runAlusRevenge(driver, log=getLogger()):
    locateSwagBucksWindow(driver)
    # closeExpressVPN()
    log.info('Starting Alus Revenge')
    driver.webDriver.get('https://www.swagbucks.com/games/play/319/alu-s-revenge-2?tid=113')
    time.sleep(2)
    Alu = pygetwindow.getWindowsWithTitle("Alu's Revenge 2 - Free Online Games | Swagbucks - Google Chrome")[0] # move window to primary monitor
    Alu.moveTo(10, 10); Alu.resizeTo(100, 100); Alu.maximize()
    driver.getElementAndClick('id', 'gamesItemBtn', wait=20) # Play for Free
    time.sleep(3)
    pageBody = driver.getElement('xpath', "/html/body")
    # pageBody.send_keys(Keys.DOWN);   pageBody.send_keys(Keys.DOWN);   pageBody.send_keys(Keys.DOWN)
    redeemed = 0
    totalGames = 0
    while redeemed < 3 and totalGames < 8:
        # num = 0
        pyautogui.leftClick(850, 950);  pyautogui.leftClick(850, 950);  time.sleep(2) # click Play Now
        pyautogui.leftClick(938, 775);  pyautogui.leftClick(938, 775);  time.sleep(2) # click Play Now (again)
        pyautogui.leftClick(872, 890);  pyautogui.leftClick(872, 890);  time.sleep(4) # click to remove "goal screen" and start game
        pyautogui.leftClick(680, 965);  pyautogui.leftClick(680, 965);  pyautogui.leftClick(750, 965);  pyautogui.leftClick(825, 965)   # click tiles
        pyautogui.leftClick(900, 965);  pyautogui.leftClick(975, 965);  pyautogui.leftClick(1025, 965); 
        # time.sleep(25)
        # while num < 5:
        game_over_text = driver.getElementText('xpath', "//*[@id='embedGameOverHdr']/h3", wait=30)
        if game_over_text:
            log.info('game over text seen')
            if game_over_text != "No SB this time. Keep trying...": 
                log.info('clicked play for free')
                redeemed += 1
            driver.getElementAndClick('id', 'gamePlayAgainBtn') # play again
            time.sleep(3)
        totalGames+=1
                # break
            # num += 1
    if redeemed == 3:
        log.info('Alus revenge successful')
    else:
        log.warning(f'Only redeemed Alus revenge {str(redeemed)} times')

def dailyPoll(driver):
    driver.openNewWindow('https://www.swagbucks.com/polls');    time.sleep(1)
    if driver.getElementAndClick('css_selector', "td.pollCheckbox", wait=2): # try first answer
        driver.getElementAndClick('id', "btnVote", wait=2) # vote & earn

def toDoList(driver):
    list_item_num, button_num, button_not_clicked, main = 1, 2, True, driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1]
    closePopUps(driver)
    while list_item_num <= 8:
        if not driver.getElement('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[1]/h4", wait=2): # look for Daily Bonus header
            driver.getElementAndClick('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/button/span", wait=2) # click to show To Do List
        time.sleep(1)
        list_item = driver.getElement('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[2]/div/section[1]/div/ul/li[" + str(list_item_num) + "]/a", wait=2)
        if list_item.text == "Add A Magic Receipts Offer":
            driver.webDriver.get("https://www.swagbucks.com/grocery-receipts-merchant?category=-1&merchant-id=53"); time.sleep(4)
            while button_not_clicked:
                button = driver.getElement('xpath', getSwagbucksBasePath() + "2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/section[4]/ul/li[" + str(button_num) +"]/div/a/div[2]/button/span", wait=2)
                if not button:
                    button = driver.getElement('xpath', getSwagbucksBasePath() + "2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/section[4]/ul/li[" + str(button_num) +"]/div/a/div[3]/button/span", wait=2, allowFail=False)
                    if not button:
                        print("FAILED TO ADD MAGIC RECEIPT")
                        break
                if button.text == 'Add to List':    
                    button.click(); button_not_clicked = False                    
                else:                               
                    button_num+=1
            driver.webDriver.get('https://www.swagbucks.com/'); time.sleep(2)
        elif list_item.text == "Deal of the Day" or list_item.text == "Game Of The Day":
            window_num_before = len(driver.webDriver.window_handles)
            list_item.click()
            time.sleep(6)
            window_num_after = len(driver.webDriver.window_handles)
            if window_num_before == window_num_after:   driver.webDriver.get('https://www.swagbucks.com/')
            else:
                driver.switchToLastWindow()
                driver.webDriver.close()
                driver.webDriver.switch_to.window(main)
        list_item_num += 1

def swagbucksInbox(driver):
    def openAndCloseInboxItem(driver):
        driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[5]/div[1]/div[1]/div/a")
        time.sleep(2)
        driver.switchToLastWindow()
        driver.webDriver.close()
        driver.switchToLastWindow()
    
    driver.openNewWindow('https://www.swagbucks.com/g/inbox')
    while True:
        closePopUps(driver)
        if not driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/a/div[2]", wait=2): # Inbox Item
            break
        description = driver.getElementText('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/h1", wait=2)
        if "Earn Every" in description: 
            openAndCloseInboxItem(driver)
        elif "Discover Daily Interests" in description:
            num = 0
            while num < 4:  openAndCloseInboxItem(driver); num += 1
        if not driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[3]/div[2]/div[2]", wait=2): # delete
            driver.getElementAndClick('xpath', getSwagbucksBasePath() + '3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/div/span') # checkbox
            driver.getElementAndClick('id', 'deleteMessageCta') # delete
        time.sleep(1)
        alert = driver.webDriver.switch_to.alert;   alert.accept()

def swagbucksSearch(driver, log=getLogger()):
    locateSwagBucksWindow(driver)
    num = 0
    while num < 30:
        search_term1 = None
        if driver.getElement('xpath', "//*[@id='tblAwardBannerAA']/div[2]/div/div[1]/form/input[2]", wait=2):
            if driver.getElementAndClick('id', 'claimSearchWinButton', wait=2, allowFail=False):
                log.info(f'Redeemed search win in {str(num)} searches')
            break
        else:
            time.sleep(1)
            closePopUps(driver)
            driver.getElementAndClick('id', 'sbLogoLink')
            time.sleep(1)
            while search_term1 is None: search_term1 = RandomWords().get_random_word()
            driver.getElementAndSendKeys('id', 'sbGlobalNavSearchInputWeb', search_term1)
            driver.getElementAndSendKeys('id', 'sbGlobalNavSearchInputWeb', Keys.ENTER)
            time.sleep(random.choice([3, 4, 5]))
            num += 1

def getSwagBucksBalance(driver):
    locateSwagBucksWindow(driver)
    rawBalance = driver.getElementText('xpath', getSwagbucksBasePath() + "1]/header/nav/section[2]/div[1]/p/var", wait=2, allowFail=False)
    if rawBalance:
        return rawBalance.replace('SB', '').replace(',', '')

def claimSwagBucksRewards(driver, account):
    if int(account.balance) < 10030:
        print('Not enough Swagbucks to redeem')
        return False
    locateSwagBucksWindow(driver)
    driver.webDriver.get("https://www.swagbucks.com/p/prize/34668/PayPal-100")
    # time.sleep(4)
    driver.getElementAndClick('id', "redeemBtnHolder") # Claim Reward
    driver.getElementAndClick('id', "redeemBtn") # Claim a Gift Card
    driver.getElementAndClick('id', "confirmOrderCta") # Confirm (order details)
    driver.getElementAndSendKeys('id', "securityQuestionInput", 'Tiger')
    driver.getElementAndClick('id', "verifyViaSecurityQuestionCta") # click Submit

def runSwagbucks(driver, runAlu, account, book, runSearch=False, log=getLogger()):
    locateSwagBucksWindow(driver)
    if runAlu:  runAlusRevenge(driver)
    dailyPoll(driver)
    swagbucksInbox(driver)
    toDoList(driver)
    # swagBuckscontentDiscovery(driver)
    account.setBalance(getSwagBucksBalance(driver))
    book.updateMRBalance(account)
    if runSearch:   swagbucksSearch(driver)
    claimSwagBucksRewards(driver, account)
    return True
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Swagbucks = Security("Swagbucks", book)
    # locateSwagBucksWindow(driver)
    swagBuckscontentDiscovery(driver)
    driver.closeWindowsExcept([':8000/'])
    book.closeBook()
            
    
