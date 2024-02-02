import random
import time

import pyautogui
import pygetwindow
from random_words import RandomWords
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
    from Functions.GeneralFunctions import showMessage
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage

def getSwagbucksBasePath():
    return '/html/body/div[2]/div[' 
    
def closePopUps(driver):
    try:
        driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/section/section/aside/button[2]").click() # Yay for me
    except NoSuchElementException:
        try:
            driver.webDriver.find_element(By.ID, "lightboxExit").click() # to exit pop-up
        except (NoSuchElementException, ElementNotInteractableException):
            exception = "caught"

def locateSwagBucksWindow(driver):
    found = driver.findWindowByUrl("swagbucks.com")
    if not found:
        swagBucksLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def swagBucksLogin(driver):
    driver.openNewWindow('https://www.swagbucks.com/')
    try:
        driver.webDriver.find_element(By.ID, "lightboxExit").click()
    except (ElementNotInteractableException, NoSuchElementException):
        exception = "caught"
        
def swagBuckscontentDiscovery(driver):
    driver.openNewWindow("https://www.swagbucks.com/discover/alloffers?sort=2")
    cardNum = 1
    closePopUps(driver)
    while True:
        contentPath = getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[2]/div[1]/section[" + str(cardNum) + "]"
        try:
            try:
                earnings = driver.webDriver.find_element(By.XPATH, contentPath + "/p/span/span[3]").text
            except NoSuchElementException:
                cardNum += 1
                continue
            description = driver.webDriver.find_element(By.XPATH, contentPath + "/button").text
            if "1 sb" in earnings.lower() or "check out the latest deals" == description.lower():
                clickAmt = 1
                while clickAmt < 5:
                    driver.webDriver.find_element(By.XPATH, contentPath).click()
                    driver.webDriver.find_element(By.XPATH, "/html/body/aside[2]/div/div[1]/div[2]/div[2]/div/div[2]/a").click() # get SB
                    time.sleep(1)
                    driver.webDriver.find_element(By.XPATH, "/html/body/aside[2]/div/button").click() # X to close
                    clickAmt += 1
                    if "discover daily interests" != description.lower():
                        break
            elif "sb per" in earnings.lower() or int(earnings.lower().replace(" sb", '')) > 4:
                break
            cardNum += 1
        except NoSuchElementException:
            if cardNum == 1:
                showMessage('failed to find content discovery', 'check script for correct element')
            else:
                break
    driver.closeWindowsExcept([':8000/'])

def runAlusRevenge(driver):
    # closeExpressVPN()
    driver.webDriver.get('https://www.swagbucks.com/games/play/319/alu-s-revenge-2?tid=113')
    time.sleep(2)
    Alu = pygetwindow.getWindowsWithTitle("Alu's Revenge 2 - Free Online Games | Swagbucks - Google Chrome")[0] # move window to primary monitor
    Alu.moveTo(10, 10)
    Alu.resizeTo(100, 100)          
    Alu.maximize()
    driver.clickIDElementOnceAvaiable('gamesItemBtn', 20) # Play for Free
    time.sleep(3)
    element = driver.webDriver.find_element(By.XPATH,"/html/body")
    element.send_keys(Keys.DOWN)
    element.send_keys(Keys.DOWN)
    element.send_keys(Keys.DOWN)
    redeemed = 0
    while redeemed < 3:
        game_over_text = ""
        num = 0
        # click Play Now
        pyautogui.leftClick(850, 950)
        pyautogui.leftClick(850, 950)
        time.sleep(2)
        # click Play Now (again)
        pyautogui.leftClick(938, 795)
        pyautogui.leftClick(938, 795)            
        time.sleep(2)
        # click to remove "goal screen" and start game
        pyautogui.leftClick(872, 890)
        pyautogui.leftClick(872, 890)            
        time.sleep(4)
        # click tiles
        pyautogui.leftClick(680, 980)
        pyautogui.leftClick(680, 980)
        pyautogui.leftClick(750, 980)
        pyautogui.leftClick(825, 980)
        pyautogui.leftClick(900, 980)
        pyautogui.leftClick(975, 980)
        pyautogui.leftClick(1025, 980)
        time.sleep(25)
        while num < 5:
            if driver.webDriver.find_element(By.ID, "closeEmbedContainer"): # Game over screen up
                time.sleep(5)
                game_over_text = driver.webDriver.find_element(By.XPATH, "//*[@id='embedGameOverHdr']/h3").text
                if game_over_text != "":
                    if game_over_text != "No SB this time. Keep trying...":
                        redeemed += 1
                    driver.webDriver.find_element(By.ID, "gamePlayAgainBtn").click() # play again
                    time.sleep(3)
                    break
            num += 1

def dailyPoll(driver):
    driver.openNewWindow('https://www.swagbucks.com/polls')
    time.sleep(1)
    try:
        driver.webDriver.find_element(By.CSS_SELECTOR, "td.pollCheckbox").click() # first answer
        driver.webDriver.find_element(By.ID, "btnVote").click() # vote & earn
    except NoSuchElementException:
        exception = "already answered"

def toDoList(driver):
    main = driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1]
    list_item_num = 1
    button_num = 2
    button_not_clicked = True
    closePopUps(driver)
    while list_item_num <= 8:
        try:  # look for Daily Bonus header 
            driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[1]/h4")
        except NoSuchElementException:
            try: # if not visible, click to show To Do List
                driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "1]/header/nav/div[3]/button").click()
            except (NoSuchElementException, ElementClickInterceptedException):
                exception = "caught"
        time.sleep(1)
        list_item = driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "1]/header/nav/div[3]/div/div/div/div[2]/div/section[1]/div/ul/li[" + str(list_item_num) + "]/a")
        if list_item.text == "Add A Magic Receipts Offer":
            driver.webDriver.get("https://www.swagbucks.com/grocery-receipts-merchant?category=-1&merchant-id=53")
            time.sleep(4)
            while button_not_clicked:
                button = driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "2]/div[2]/div[2]/main/reset-styles/div/div/div[2]/div[1]/section[4]/ul/li[" + str(button_num) +"]/div/a/div[2]/button/span")
                if button.text == 'Add to List':
                    button.click()
                    button_not_clicked = False
                else:
                    button_num+=1
            driver.webDriver.get('https://www.swagbucks.com/')
            time.sleep(2)
        elif list_item.text == "Deal of the Day":
            window_num_before = len(driver.webDriver.window_handles)
            list_item.click()
            time.sleep(6)
            window_num_after = len(driver.webDriver.window_handles)
            if window_num_before == window_num_after:
                driver.webDriver.get('https://www.swagbucks.com/')
            else:
                driver.switchToLastWindow()
                driver.webDriver.close()
                driver.webDriver.switch_to.window(main)
        list_item_num += 1

def swagbucksInbox(driver):
    def openAndCloseInboxItem(driver):
        driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[5]/div[1]/div[1]/div/a").click()
        time.sleep(2)
        driver.switchToLastWindow()
        driver.webDriver.close()
        driver.switchToLastWindow()
    
    driver.openNewWindow('https://www.swagbucks.com/g/inbox')
    while True:
        closePopUps(driver)
        try: 
            contentPath = getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div/a/div[2]/span"
            try:
                driver.webDriver.find_element(By.XPATH, contentPath).click()
                description = driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/div[1]/div[1]/main/h1").text
                if "Earn Every" in description:
                    openAndCloseInboxItem(driver)
                elif "Discover Daily Interests" in description:
                    num = 0
                    while num < 4:
                        openAndCloseInboxItem(driver)
                        num += 1
                driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[3]/div[2]/div[2]").click() # delete
            except ElementNotInteractableException: # description is blank
                driver.webDriver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/div/span').click() # checkbox
                driver.webDriver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[1]/div[1]/main/div/div[1]/div[2]/button[2]').click() # delete
            time.sleep(1)
            alert = driver.webDriver.switch_to.alert
            alert.accept()
        except NoSuchElementException:
            exception = "no element found in inbox"
            break

def swagbucksSearch(driver):
    locateSwagBucksWindow(driver)
    driver = driver.webDriver
    num = 0
    while num < 1:
        search_term1 = None
        search_term2 = None
        search_term = None
        try:
            # accept reward
            driver.find_element(By.XPATH, "//*[@id='tblAwardBannerAA']/div[2]/div/div[1]/form/input[2]")
            num += 1
            driver.find_element(By.ID, "claimSearchWinButton").click()
        # if no reward, continue searching
        except NoSuchElementException:
            time.sleep(1)
            try:
                driver.find_element(By.ID, "sbLogoLink").click()
            # pop-up in the way
            except ElementClickInterceptedException:
                closePopUps(driver)
                driver.find_element(By.ID, "sbLogoLink").click()
            time.sleep(1)
            while search_term1 is None:
                search_term1 = RandomWords().random_word()
            while search_term2 is None:
                search_term2 = RandomWords().random_word()
            search_term = search_term1 + " " + search_term2
            driver.find_element(By.ID, "sbGlobalNavSearchInputWeb").send_keys(search_term + Keys.ENTER)
            time.sleep(random.choice([2, 3, 4]))
        except NoSuchWindowException:
            num = 3
        except WebDriverException:
            num = 3

def getSwagBucksBalance(driver):
    locateSwagBucksWindow(driver)
    return driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "1]/header/nav/section[2]/div[1]/p/var").text.replace('SB', '').replace(',', '')

def claimSwagBucksRewards(driver):
    locateSwagBucksWindow(driver)
    driver = driver.webDriver
    # Paypal $10 rewards page
    driver.get("https://www.swagbucks.com/p/prize/28353/PayPal-10")
    time.sleep(4)
    driver.find_element(By.ID,"redeemBtnHolder").click() # Claim Reward
    driver.find_element(By.ID,"redeemBtn").click() # Claim a Gift Card
    driver.find_element(By.ID,"confirmOrderCta").click() # Confirm (order details)
    driver.find_element(By.ID,"securityQuestionInput").send_keys("Tiger") 
    driver.find_element(By.ID,"verifyViaSecurityQuestionCta").click() # click Submit

def runSwagbucks(driver, runAlu, account, book):
    # closeExpressVPN()
    locateSwagBucksWindow(driver)
    if runAlu:
        runAlusRevenge(driver)
    dailyPoll(driver)
    swagbucksInbox(driver)
    toDoList(driver)
    swagBuckscontentDiscovery(driver)
    account.setBalance(getSwagBucksBalance(driver))
    book.updateMRBalance(account)
    if int(account.balance) > 1000:
        claimSwagBucksRewards(driver)
    swagbucksSearch(driver)
    
# if __name__ == '__main__':
#     driver = Driver("Chrome")
#     book = GnuCash('Finance')
#     Swagbucks = Security("Swagbucks", book)
#     runSwagbucks(driver, False, Swagbucks, book)
#     book.closeBook()

if __name__ == '__main__':
    driver = Driver("Chrome")
    locateSwagBucksWindow(driver)
    runAlusRevenge(driver)

