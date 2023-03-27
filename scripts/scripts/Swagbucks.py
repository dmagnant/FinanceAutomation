import random
import time
import threading

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
    from Classes.Asset import Crypto
    from Functions.GeneralFunctions import showMessage
    from Functions.GnuCashFunctions import openGnuCashBook
else:
    from .Classes.Asset import Crypto
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import openGnuCashBook

def getSwagbucksBasePath():
    return '/html/body/div[2]/div[' 
    
def closePopUps(driver):
    driver.webDriver.implicitly_wait(2)
    try:
        # click Yay for me
        driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/section/section/aside/button[2]").click()
    except NoSuchElementException:
        try:
            # Exit Generic Pop-up Box
            driver.webDriver.find_element(By.ID, "lightboxExit").click()
        except NoSuchElementException:
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
    driver.openNewWindow("https://www.swagbucks.com/discover/explore")
    driver.webDriver.find_element(By.ID,"sbShopSort").click()     # filter min to max
    driver.webDriver.find_element(By.XPATH,"//*[@id='sbShopSort']/option[4]").click() # filter min to max
    cardNum = 1
    closePopUps(driver)
    while True:
        contentPath = getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div[2]/div[1]/section[" + str(cardNum) + "]"
        try:
            try:
                earnings = driver.webDriver.find_element(By.XPATH, contentPath + "/p/span/span[3]").text
            except NoSuchElementException:
                if cardNum <=2:
                    cardNum+=1
                    continue
                else:
                    break
            description = driver.webDriver.find_element(By.XPATH, contentPath + "/button").text
            if "1 sb" in earnings.lower() or "discover daily interests" == description.lower():
                clickAmt = 1
                while clickAmt < 5:
                    driver.webDriver.find_element(By.XPATH, contentPath).click()
                    # click get SB
                    driver.webDriver.find_element(By.XPATH, "/html/body/aside[2]/div/div[1]/div[2]/div[2]/div/div[2]/a").click()
                    time.sleep(1)
                    # click X to close
                    driver.webDriver.find_element(By.XPATH, "/html/body/aside[2]/div/button").click()
                    clickAmt += 1
                    if "discover daily interests" != description.lower():
                        break
            elif int(earnings.lower().replace(" sb", '')) > 4:
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
    driver.get('https://www.swagbucks.com/games/play/319/alu-s-revenge-2?tid=113')
    time.sleep(2)
    Alu = pygetwindow.getWindowsWithTitle("Alu's Revenge 2 - Free Online Games | Swagbucks - Google Chrome")[0] # move window to primary monitor
    Alu.moveTo(10, 10)
    Alu.resizeTo(100, 100)          
    Alu.maximize()
    driver.implicitly_wait(20)
    driver.find_element(By.ID, "gamesItemBtn").click() # Play for Free
    time.sleep(3)
    driver.find_element(By.XPATH,"/html/body").send_keys(Keys.DOWN)
    driver.find_element(By.XPATH,"/html/body").send_keys(Keys.DOWN)
    driver.find_element(By.XPATH,"/html/body").send_keys(Keys.DOWN)
    driver.find_element(By.XPATH,"/html/body").send_keys(Keys.UP)
    redeemed = 0
    while redeemed < 2:
        game_over_text = ""
        num = 0
        # click Play Now
        pyautogui.leftClick(850, 950)
        pyautogui.leftClick(850, 950)
        time.sleep(1)
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
            if driver.find_element(By.ID, "closeEmbedContainer"): # Game over screen up
                time.sleep(5)
                game_over_text = driver.find_element(By.XPATH, "//*[@id='embedGameOverHdr']/h3").text
                if game_over_text != "":
                    if game_over_text != "No SB this time. Keep trying...":
                        redeemed += 1
                    driver.find_element(By.ID, "gamePlayAgainBtn").click() # play again
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
    button_num = 1
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
            list_item.click()
            time.sleep(2)
            while button_not_clicked:
                try:
                    driver.webDriver.find_element(By.XPATH, getSwagbucksBasePath() + "3]/div[3]/div[1]/main/div/div[2]/div[2]/div[2]/div/div/a[" + str(button_num) +"]/div[2]/button[1]").click()
                    button_not_clicked = False
                except ElementNotInteractableException:
                    button_num += 1
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
            contentPath = getSwagbucksBasePath() + "3]/div[1]/div[1]/main/div/div[2]/div/div[3]/div[1]/a/div[2]/span"
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
            time.sleep(1)
            alert = driver.webDriver.switch_to.alert
            alert.accept()
        except NoSuchElementException:
            exception = "no element found in inbox"
            break

def swagbucksSearch(driver):
    locateSwagBucksWindow(driver)
    driver = driver.webDriver
    driver.implicitly_wait(3)
    delay = [1, 2, 3]
    searches = 0
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
            searches += 1
            while search_term1 is None:
                search_term1 = RandomWords().random_word()
            while search_term2 is None:
                search_term2 = RandomWords().random_word()
            search_term = search_term1 + " " + search_term2
            driver.find_element(By.ID, "sbGlobalNavSearchInputWeb").send_keys(search_term + Keys.ENTER)
            time.sleep(random.choice(delay))
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
    # Claim Reward
    driver.find_element(By.ID,"redeemBtnHolder").click()
    # Claim a Gift Card
    driver.find_element(By.ID,"redeemBtn").click()
    # Confirm (order details)
    driver.find_element(By.ID,"confirmOrderCta").click()
    # enter childhood nickname
    driver.find_element(By.ID,"securityQuestionInput").send_keys("Tiger")
    # click Submit
    driver.find_element(By.ID,"verifyViaSecurityQuestionCta").click()

def runSwagbucks(driver, runAlu, account, book):
    # closeExpressVPN()
    driver.webDriver.implicitly_wait(2)
    locateSwagBucksWindow(driver)
    if runAlu:
        runAlusRevenge(driver.webDriver)
    dailyPoll(driver)
    swagbucksInbox(driver)
    toDoList(driver)
    swagBuckscontentDiscovery(driver)
    account.setBalance(getSwagBucksBalance(driver))
    account.updateMRBalance(book)
    if int(account.balance) > 1000:
        claimSwagBucksRewards(driver)
    swagbucksSearch(driver)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = openGnuCashBook('Finance', False, False)
    Swagbucks = Crypto("Swagbucks", book)
    runSwagbucks(driver, False, Swagbucks, book)
    if not book.is_saved:
        book.save()
    book.close()
    