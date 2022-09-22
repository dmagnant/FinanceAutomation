import os
import time

import pyautogui
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys
sys.path.append("..")
from ..Functions import getPassword, getUsername, setDirectory, openWebDriver


def login(directory, driver, bingWindow):
    driver.switch_to.window(bingWindow)
    driver.maximize_window()
    time.sleep(1)
    # login
    try:
        # click Sign in
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/section/div[1]/div[2]/section/div[1]/a[2]").click()
        # enter username
        driver.find_element(By.ID, "i0116").send_keys(getUsername(directory, 'Bing Rewards'))
        time.sleep(1)
        # click Next
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(1)
        # enter password
        driver.find_element(By.ID, "i0118").send_keys(getPassword(directory, 'Bing Rewards'))
        time.sleep(1)
        # click Sign in
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(1)
        # click to stay signed in
        driver.find_element(By.XPATH, "/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[2]/input").click()
        # click sign in link
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/main/section/div[1]/div[2]/section/div[1]/a[2]").click()
    except NoSuchElementException:
        exception = "already logged in"


def performRewardActivities(driver, bingWindow):
    # gather "points" links
    # pointsLinks = driver.find_elements(By.CSS_SELECTOR, "mee-rewards-daily-set-item-content")
    pointsLinks = driver.find_elements(By.CSS_SELECTOR, "div.actionLink.x-hidden-vp1")

    # click on first link
    pointsLinks[0].click()
    time.sleep(1)
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(1)
    driver.close()
    driver.switch_to.window(bingWindow)

    # click on Daily Poll
    pointsLinks[2].click()
    time.sleep(1)
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        if driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/span/a'):
            time.sleep(1)
            driver.close()
            driver.switch_to.window(bingWindow)
            time.sleep(1)
            pointsLinks[2].click()
            # switch to last window
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    except NoSuchElementException:
        exception = "caught"
    time.sleep(2)
    pyautogui.leftClick(350, 950)
    time.sleep(2)
    # click multiple choice option
    pyautogui.leftClick(1225, 925)
    # click True/False option
    # click True
    pyautogui.leftClick(350, 950)
    time.sleep(1)
    # click False
    pyautogui.leftClick(425, 950)
    driver.close()
    driver.switch_to.window(bingWindow)

def claimRewards(driver):
    # capture balance
    time.sleep(3)
    bingBalance = driver.find_element(By.XPATH, "//*[@id='rewardsBanner']/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span").text.replace(',', '')
    if int(bingBalance) >= 5250:
        # go to $5 Amazon gift card link
        driver.get("https://rewards.microsoft.com/redeem/000800000000")
        time.sleep(3)
        # click Redeem Reward
        driver.find_element(By.XPATH, "//*[@id='redeem-pdp_000800000000']/span[1]").click()
        time.sleep(3)
        # click Confirm Reward
        driver.find_element(By.XPATH, "//*[@id='redeem-checkout-review-confirm']/span[1]").click()
        try:
            # enter Phone number
            driver.find_element(By.ID, "redeem-checkout-challenge-fullnumber").send_keys(os.environ.get('Phone'))
            # click Send
            driver.find_element(By.XPATH, "//*[@id='redeem-checkout-challenge-validate']/span").click()
        except NoSuchElementException:
            exception = "caught"


def runBing(directory, driver):
    driver.get('https://rewards.microsoft.com/')
    bingWindow = driver.window_handles[0]
    login(directory, driver, bingWindow)
    performRewardActivities(driver, bingWindow)
    claimRewards(driver)

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Edge")
    driver.implicitly_wait(3)
    runBing(directory, driver)
