import random, time, pyautogui, pygetwindow
from random_word import RandomWords
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        NoSuchWindowException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

if __name__ == '__main__' or __name__ == "Swagbucks":
    from Classes.WebDriver import Driver
    from Classes.MobileDriver import Mobile
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, setDirectory, getLogger, putWindowInFocus, minimizeAllWindowsExcept
else:
    from .Classes.Asset import Security
    from .Classes.MobileDriver import Mobile
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, setDirectory, getLogger, putWindowInFocus, minimizeAllWindowsExcept

def getSwagbucksBasePath(): return '/html/body/div[2]/div['
    
def closeSwagbucksPopUps(driver):
    driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/section/section/aside/button[2]", wait=0.1)  # Yay for me
    driver.getElementAndClick('xpath', "/html/body/reset-styles/div/div[1]/aside/div/button[1]", wait=0.1)  # to exit pop-up
    driver.getElementAndClick('id', 'lightboxExit', wait=0.1) # to exit pop-up

def locateSwagBucksWindow(driver):
    found = driver.findWindowByUrl("swagbucks.com")
    if not found:   swagBucksLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(0.5)
    closeSwagbucksPopUps(driver)

def consolidateSwagbucksWindows(driver):
    mainHandle = driver.findWindowByUrl('https://www.swagbucks.com/')
    for handle in driver.webDriver.window_handles:
        if handle != mainHandle:
            driver.webDriver.switch_to.window(handle)
            driver.webDriver.close()
    driver.webDriver.switch_to.window(mainHandle)


def swagBucksLogin(driver):
    driver.openNewWindow('https://www.swagbucks.com/')
        
def swagBuckscontentDiscovery(driver):
    driver.openNewWindow("https://www.swagbucks.com/discover-new/explore")
    contentDiscoverWindow = driver.webDriver.current_window_handle
    closeSwagbucksPopUps(driver)
    windowCount = driver.getWindowCount()
    cycleThroughSwagbucksOffers(driver, f"{getSwagbucksBasePath()}2]/div[2]/div[2]/main/div[3]/div[2]/div[2]/div/div/ul/li[cardNum]/section/div", contentDiscoverWindow, windowCount) # featured offers
    cycleThroughSwagbucksOffers(driver, f"{getSwagbucksBasePath()}2]/div[2]/div[2]/main/div[3]/section[2]/ul/li[cardNum]", contentDiscoverWindow, windowCount) # explore web content and earn
    driver.closeWindowsExcept([':8000/'])

def cycleThroughSwagbucksOffers(driver, offerPath, contentDiscoverWindow, windowCount):
    cardNum = 1
    while True:
        modifiedOfferPath = offerPath.replace('cardNum', str(cardNum))
        offer = driver.getElement('xpath', modifiedOfferPath, wait=0.5) # click to open
        if not offer: 
            print("failed to find offer element")
            return False
        reviewSwagbucksOffer(driver, offer, contentDiscoverWindow, windowCount)
        cardNum += 1

def reviewSwagbucksOffer(driver, offer, contentDiscoverWindow, windowCount):
    print(offer.text)
    if "1 sb" in offer.text.lower():
        offer.click()
        driver.getElementAndClick('xpath', "/html/body/div[3]/reset-styles/div[1]/div/aside/div/div[2]/a/span", wait=0.5) # Earn SB
        time.sleep(1)
        newWindowCount = driver.getWindowCount()
        if newWindowCount > windowCount:
            driver.webDriver.switch_to.window(contentDiscoverWindow)
        driver.getElementAndClick('xpath', "/html/body/div[3]/reset-styles/div[1]/div/aside/div/button", wait=0.5) # X to close

def runHamsterRun(driver, log=getLogger()):
    locateSwagBucksWindow(driver)
    driver.webDriver.get("https://www.swagbucks.com/games/play/giant-hamster-run")
    driver.getElementAndClick('xpath', "//*[@id='scrollable-content']/main/div[3]/div[2]/div/button/span", wait=0.50) # Play for Free
    gamesWon = 0
    gamesAttempted = 0
    while gamesWon < 3 and gamesAttempted < 8:
        time.sleep(12)
        print(f'Games won: {str(gamesWon)} out of {str(gamesAttempted)} attempted')
        pyautogui.leftClick(575, 950)
        num = 1
        while num < 15:
            pyautogui.press('up')
            time.sleep(2)
            num += 1
        gameOverText = driver.getElementText('xpath', "//*[@id='modals-container']/div/aside/div/div/div[1]/p", wait=10)
        if 'No SB this time' not in gameOverText:
            gamesWon += 1
        driver.getElementAndClick('xpath', "//*[@id='modals-container']/div/aside/div/div/div[2]/button/span") # Try Again
        gamesAttempted += 1
    driver.webDriver.get('https://www.swagbucks.com/')
    # print("Daily Games attempted")
    # log.info("Daily Games Attempted")

def runAlusRevenge(driver, log=getLogger()):
    locateSwagBucksWindow(driver)
    # closeExpressVPN()
    log.info('Starting Alus Revenge')
    driver.webDriver.get('https://www.swagbucks.com/games/play/319/alu-s-revenge-2?tid=113')
    time.sleep(2)
    Alu = pygetwindow.getWindowsWithTitle("Alu's Revenge 2 - Free Online Games | Swagbucks - Google Chrome")[0] # move window to primary monitor
    Alu.moveTo(10, 10); Alu.resizeTo(100, 100); Alu.maximize()
    driver.getElementAndClick('id', 'gamesItemBtn', wait=0.50) # Play for Free
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
    main = driver.findWindowByUrl('https://www.swagbucks.com/')
    driver.openNewWindow('https://www.swagbucks.com/polls');    time.sleep(1)
    driver.getElementAndClick('xpath', "//*[@id='answer1']/table/tbody/tr/td[2]/table/tbody/tr/td", wait=0.5) # try first answer
    driver.getElementAndClick('xpath', "/html/body/div[2]/div[2]/div[2]/div[2]/main/section/div/div[1]/div/form/ul/li[1]/label") # try diff format
    driver.getElementAndClick('xpath', "//*[@id='scrollable-content']/main/section/div/div[1]/div/form/button", wait=0.5) # vote & earn
    driver.webDriver.switch_to.window(main)

def getToDoListButton(driver):
    toDoListButton = driver.getElement('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]", wait=0.3)
    if toDoListButton:
        return {'button': toDoListButton, 'format': 1}
    toDoListButton = driver.getElementAndClick('xpath', getSwagbucksBasePath() + "2]/div[1]/div[1]/header/div/div[3]", wait=0.3) # click to show To Do List (alt format)
    if toDoListButton:
        return {'button': toDoListButton, 'format': 2}
    else:
        return False
    
def getToDoListItem(driver, format, list_item_num):
    if format == 1:
        list_item = driver.getElement('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[2]/div/section[1]/div/ul/li[" + str(list_item_num) + "]", wait=0.3)
    elif format == 2:
        list_item = driver.getElement('xpath', getSwagbucksBasePath() + "2]/div[1]/div[1]/header/div/div[3]/section/div/div[1]/div/div/section[1]/div/ul/li[" + str(list_item_num) + "]", wait=0.3)
    return list_item

def swagBucksToDoList(driver, log=getLogger()):
    list_item_num, button_num, button_not_clicked, mainHandle = 1, 2, True, driver.findWindowByUrl('https://www.swagbucks.com/')
    closeSwagbucksPopUps(driver)
    toDoListButton = getToDoListButton(driver)
    if not toDoListButton:
        print('failed to find the to do list button')
        log.error('failed to find the to do list button')
        return False
    while list_item_num <= 8:
        list_item = getToDoListItem(driver, toDoListButton['format'], list_item_num)
        if not list_item:
            print('not found initially, clicking button to show to do list')
            try:
                toDoListButton['button'].click()
            except StaleElementReferenceException:
                toDoListButton = getToDoListButton(driver)
                print(toDoListButton)
                toDoListButton['button'].click()
            time.sleep(1)
            list_item = getToDoListItem(driver, toDoListButton['format'], list_item_num)
        if not list_item:
            print('failed to find the to do list item')
            log.error('failed to find the to do list item')
            return False
        print(list_item.text)
        if list_item.text == "Add A Magic Receipts Offer":
            driver.openNewWindow('https://www.swagbucks.com/grocery-receipts-merchant?category=-1&merchant-id=53')
            time.sleep(4)
            while button_not_clicked:
                button = driver.getElement('xpath', getSwagbucksBasePath() + "2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/section[4]/ul/li[" + str(button_num) +"]/div/a/div[2]/button/span", wait=0.5)
                if not button:
                    button = driver.getElement('xpath', getSwagbucksBasePath() + "2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/section[4]/ul/li[" + str(button_num) +"]/div/a/div[3]/button/span", wait=0.5, allowFail=False)
                    if not button:
                        print("FAILED TO ADD MAGIC RECEIPT")
                        break
                if button.text == 'Add to List':    
                    button.click(); button_not_clicked = False                    
                else:                               
                    button_num+=1
            driver.webDriver.switch_to.window(mainHandle); time.sleep(2)
        elif "Deal of the Day" in list_item.text or "Game Of The Day" in list_item.text:
            if 'Deal' in list_item.text:
                driver.getElementAndClick('partial_link_text', 'Deal of the Day', wait=0.2)
            elif 'Game' in list_item.text:
                driver.getElementAndClick('partial_link_text', 'Game Of The Day', wait=0.2)
            time.sleep(6)
            driver.webDriver.switch_to.window(mainHandle); time.sleep(2)
            driver.webDriver.get('https://www.swagbucks.com/')
            toDoListButton = getToDoListButton(driver)
            # window_num_after = len(driver.webDriver.window_handles)
            # if window_num_before == window_num_after:   driver.webDriver.get('https://www.swagbucks.com/')
            # else:
            #     driver.switchToLastWindow()
            #     driver.webDriver.close()
            #     driver.webDriver.switch_to.window(main)
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
        closeSwagbucksPopUps(driver)
        if not driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/a/div[2]", wait=0.5): # Inbox Item
            break
        description = driver.getElementText('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/h1", wait=0.5)
        if description:
            if "Earn Every" in description: 
                openAndCloseInboxItem(driver)
            elif "Discover Daily Interests" in description:
                num = 0
                while num < 4:  
                    openAndCloseInboxItem(driver); num += 1
        if not driver.getElementAndClick('xpath', getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[3]/div[2]/div[2]", wait=0.5): # delete
            driver.getElementAndClick('xpath', getSwagbucksBasePath() + '3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/div/span') # checkbox
            driver.getElementAndClick('id', 'deleteMessageCta') # delete
        time.sleep(1)
        alert = driver.webDriver.switch_to.alert;   alert.accept()

def getSBNeededUntilNextGoal(driver):
    locateSwagBucksWindow(driver)
    driver.webDriver.refresh()
    time.sleep(1)
    driver.getElementAndClick('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]", wait=0.3) # To do list button
    time.sleep(2)
    sbEarned = driver.getElementText('xpath', getSwagbucksBasePath() + '1]/header/nav/div[3]/div/div/div/div[2]/div/section[2]/div/div[1]/p/var', wait=0.5).replace(' SB','')
    print(f'SB earned today: {sbEarned}')
    sbGoal1 = driver.getElementText('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[2]/div/section[2]/div/div[2]/div[2]/div/div/div[2]/p[1]/var", wait=0.5).replace(' SB','')
    print(f'SB goal 1: {sbGoal1}')
    sbGoal2 = driver.getElementText('xpath', getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[2]/div/section[2]/div/div[2]/div[2]/div/div/div[3]/p[1]/var", wait=0.5).replace(' SB','')
    print(f'SB goal 2: {sbGoal2}')
    if float(sbEarned) >= float(sbGoal2):
        print('next goal already reached')
        return 0
    elif float(sbEarned) >= float(sbGoal1):
        sbNeeded = float(sbGoal2) - float(sbEarned)
    else:
        sbNeeded = float(sbGoal1) - float(sbEarned)
    print(f'SB needed until next goal: {sbNeeded}')
    return sbNeeded

def redeemSwagbucksMobileOffers(driver, offersToRedeem=1):
    if offersToRedeem == "auto":
        locateSwagBucksWindow(driver)
        offersToRedeem = getSBNeededUntilNextGoal(driver)
        if not offersToRedeem or offersToRedeem < 1:
            return
    SBmobile = Mobile("com.prodege.swagiq", "com.prodege.swagiq.android.home.HomeActivity")
    SBmobile.unlockMobileDevice()
    SBmobile.getElementAndClick('id',"com.prodege.swagiq:id/btn_earn_more") # Tap to Earn More
    time.sleep(1)
    SBmobile.getElementIfTextEquals("Tapjoy").click()
    time.sleep(1)
    SBmobile.clickAllOffers(redemptionsNeeded=offersToRedeem)
    SBmobile.driver.quit()

def swagbucksSearch(driver, log=getLogger()):
    locateSwagBucksWindow(driver)
    num = 0
    while num < 30:
        search_term1 = None
        if driver.getElement('xpath', "//*[@id='tblAwardBannerAA']/div[2]/div/div[1]/form/input[2]", wait=0.5):
            if driver.getElementAndClick('id', 'claimSearchWinButton', wait=1, allowFail=False):
                log.info(f'Redeemed search win in {str(num)} searches')
            break
        else:
            time.sleep(1)
            closeSwagbucksPopUps(driver)
            driver.getElementAndClick('id', 'sbLogoLink')
            time.sleep(1)
            while search_term1 is None: search_term1 = RandomWords().get_random_word()
            driver.getElementAndSendKeys('id', 'sbGlobalNavSearchInputWeb', search_term1)
            driver.getElementAndSendKeys('id', 'sbGlobalNavSearchInputWeb', Keys.ENTER)
            time.sleep(random.choice([3, 4, 5]))
            num += 1

def getSwagBucksBalance(driver):
    locateSwagBucksWindow(driver)
    rawBalance = driver.getElementText('xpath', getSwagbucksBasePath() + "1]/header/nav/section[2]/div[1]/p/var", wait=0.5, allowFail=False)
    if rawBalance:
        return rawBalance.replace('SB', '').replace(',', '')

def claimSwagBucksRewards(driver, account):
    account.setBalance(getSwagBucksBalance(driver))
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

def runSwagbucks(driver, dailyGame, account, book, runSearch=False, log=getLogger()):
    locateSwagBucksWindow(driver)
    if dailyGame:  runHamsterRun(driver, log)
    dailyPoll(driver)
    # swagbucksInbox(driver)
    swagBucksToDoList(driver)
    swagBuckscontentDiscovery(driver)
    account.setBalance(getSwagBucksBalance(driver))
    book.updateMRBalance(account)
    if runSearch:   swagbucksSearch(driver)
    claimSwagBucksRewards(driver, account)
    return True
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    # book = GnuCash('Finance')
    # Swagbucks = Security("Swagbucks", book)
    # locateSwagBucksWindow(driver)
    # dailyPoll(driver)
    # book.closeBook()
    # swagBucksToDoList(driver)
    # swagbucksSearch(driver)
    # runHamsterRun(driver, log=getLogger()) 

    redeemSwagbucksMobileOffers(driver, offersToRedeem="auto")

