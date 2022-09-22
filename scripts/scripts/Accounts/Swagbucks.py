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
# import os, os.path
import sys
sys.path.append("..")
from ..Functions import openWebDriver, showMessage

def login(driver):
    driver.execute_script("window.open('https://www.swagbucks.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    showMessage('test', 'test')

def contentDiscovery(driver):
    driver.execute_script("window.open('https://www.swagbucks.com/discover/explore');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    num = 1
    while (num <= 20):
        contentPath = "/html/body/div[2]/div[3]/div[1]/div[1]/main/div[2]/div[1]/section[" + str(num) + "]/button"
        description = driver.find_element(By.XPATH, contentPath + "/span").text
        if "click & earn" in description.lower():
            driver.find_element(By.XPATH, contentPath).click()
            # click get SB
            driver.find_element(By.XPATH, "/html/body/aside[2]/div/div[1]/div[2]/div[2]/div/div[2]/a").click()
            time.sleep(1)
            # click X to close
            driver.find_element(By.XPATH, "/html/body/aside[2]/div/button").click()
        # print(f'{num}: {description}')
        num += 1
    # close all extra windows
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

def runAlusRevenge(driver, run_Alu):
    if run_Alu:
        # closeExpressVPN()
        #Play Alus Revenge
        driver.get('https://www.swagbucks.com/games/play/319/alu-s-revenge-2?tid=113')
        time.sleep(2)

        # move window to primary monitor
        Alu = pygetwindow.getWindowsWithTitle("Alu's Revenge 2 - Free Online Games | Swagbucks - Google Chrome")[0]
        Alu.moveTo(10, 10)
        Alu.resizeTo(100, 100)          
        Alu.maximize()
        driver.implicitly_wait(20)
        # click Play for Free
        driver.find_element(By.ID, "gamesItemBtn").click()
        time.sleep(3)
        redeemed = 0
        while redeemed < 5:
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
                # if Game over screen up
                if driver.find_element(By.ID, "closeEmbedContainer"):
                    time.sleep(5)
                    #read response
                    game_over_text = driver.find_element(By.XPATH, "//*[@id='embedGameOverHdr']/h3").text
                    if game_over_text != "":
                        if game_over_text != "No SB this time. Keep trying...":
                            redeemed += 1
                        # click Play again
                        driver.find_element(By.ID, "gamePlayAgainBtn").click()
                        time.sleep(3)
                        break
                num += 1

def dailyPoll(driver):
    driver.execute_script("window.open('https://www.swagbucks.com/polls');")
    time.sleep(1)
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)
    try:
        # click on first answer
        driver.find_element(By.CSS_SELECTOR, "td.pollCheckbox").click()
        # click Vote & Earn
        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[5]/div[2]/div[2]/div[1]/div[1]").click()
    except NoSuchElementException:
        exception = "already answered"
    driver.close()

def openTabs(driver):
    #Inbox
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.execute_script("window.open('https://www.swagbucks.com/g/inbox');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])

def toDoList(driver):
    # To Do List
    main = driver.window_handles[len(driver.window_handles)-1]
    list_item_num = 1
    button_num = 1
    button_not_clicked = True
    while list_item_num <= 8:
        try:
            # look for Daily Bonus header 
            driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/header/nav/div[3]/div/div/div/div[1]/h4")
        except NoSuchElementException:
            try:
                # if not visible, click to show To Do List
                driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/header/nav/div[3]/button").click()
            except (NoSuchElementException, ElementClickInterceptedException):
                exception = "caught"
        time.sleep(1)
        # get title of List Item
        list_item = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/header/nav/div[3]/div/div/div/div[2]/div/section[1]/div/ul/li[" + str(list_item_num) + "]/a")
        if list_item.text == "Add A Magic Receipts Offer":
            list_item.click()
            time.sleep(2)
            while button_not_clicked:
                try:
                    driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[3]/div[1]/main/div/div[2]/div[2]/div[2]/div/div/a[" + str(button_num) +"]/div[2]/button[1]").click()
                    button_not_clicked = False
                except ElementNotInteractableException:
                    button_num += 1
        elif list_item.text == "Deal of the Day":
            window_num_before = len(driver.window_handles)
            list_item.click()
            time.sleep(6)
            window_num_after = len(driver.window_handles)
            if window_num_before == window_num_after:
                driver.get('https://www.swagbucks.com/')
            else:
                driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
                driver.close
                driver.switch_to.window(main)
        list_item_num += 1

def swagbucksSearch(driver):
    if len(driver.window_handles) > 1:
        for i in driver.window_handles:
            driver.switch_to.window(i)
            if "| Swagbucks" in driver.title:
                found = True
        if not found:
            login(driver)
    else:
        if "| Swagbucks" not in driver.title:
            login(driver)
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
            print("search rewarded")
        # if no reward, continue searching
        except NoSuchElementException:
            time.sleep(1)
            try:
                driver.find_element(By.ID, "sbLogoLink").click()
            # light-box pop-up in the way
            except ElementClickInterceptedException:
                try: 
                    driver.find_element(By.ID, "lightboxExit").click()
                except NoSuchElementException:
                    try: 
                        showMessage('Daily goal celebration test', '"YAY FOR ME" button should be clicked after clicking OK on this message')
                        driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/section/section/aside/button[2]")
                    except ElementNotInteractableException:
                        exception = "caught"
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

def runSwagbucks(driver, run_Alu):
    # closeExpressVPN()
    driver.implicitly_wait(2)
    login(driver)
    try:
        driver.find_element(By.ID, "lightboxExit").click()
    except (ElementNotInteractableException, NoSuchElementException):
        exception = "caught"
    runAlusRevenge(driver, run_Alu)
    contentDiscovery(driver)
    dailyPoll(driver)
    openTabs(driver)
    toDoList(driver)
    swagbucksSearch(driver)

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    runSwagbucks(driver, False)
