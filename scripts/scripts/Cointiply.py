import time
from matplotlib import pyplot as plt

import cv2
import numpy as np
import pyautogui
import pygetwindow
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.common.by import By

# from matplotlib import pyplot as plt

from scripts.scripts.Functions import (openWebDriver, getPassword, getUsername,
                       setDirectory, showMessage)

if __name__ == '__main__' or __name__ == "Cointiply":
    from Functions import openWebDriver, getPassword, getUsername, setDirectory, showMessage
else:
    from .Functions import getPassword, getUsername, setDirectory, showMessage

def cointiplyLogin(directory, driver):
    driver.get("https://cointiply.com/login")
    #Login
    try:
        # enter email
        driver.find_element(By.XPATH, "//html/body/div/div[2]/section/div[1]/div/div[2]/div/div[3]/form/div[1]/input").send_keys(getUsername(directory, 'Cointiply'))
        # enter password
        driver.find_element(By.XPATH, "/html/body/div/div[2]/section/div[1]/div/div[2]/div/div[3]/form/div[2]/input").send_keys(getPassword(directory, 'Cointiply'))
        showMessage("CAPTCHA", 'Verify captcha, then click OK')
        #click LOGIN
        driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/section/div[1]/div/div[2]/div/div[3]/form/div[5]/button").click()
    except NoSuchElementException:
        exception = "already logged in"
    # move window to primary monitor
    Cointiply = pygetwindow.getWindowsWithTitle('Cointiply Bitcoin Rewards - Earn Free Bitcoin - Google Chrome')[0]
    Cointiply.moveTo(10, 10)
    Cointiply.resizeTo(100, 100)
    Cointiply.maximize()

def runFaucet(driver, runFaucet):
    if runFaucet:
        # Roll Faucet
        driver.get("https://cointiply.com/home?intent=faucet")
        time.sleep(2)
        # click Roll & Win
        try:
            driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/div/button").click()
            showMessage("CAPTCHA", 'Verify captcha, then click OK')
            # click Submit Captcha & Roll
            driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[1]/div[1]/div[1]/div/div/div/button").click()
            time.sleep(3)
        except (NoSuchElementException, WebDriverException):
            exception = "gotta wait"

def watchVideos(directory, driver):
    #link from Cointiply
    # link = "https://api.lootably.com/api/offerwall/redirect/offer/101-999?placementID=ckzg5jprk003u011d0wlt2vn9&rawPublisherUserID=2193072"
    #direct link
    link = "https://loot.tv/account/login"

    driver.get(link)
    # #click login
    # driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div[2]/div/div[2]/a[1]/button").click()
    #enter email
    driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div[2]/div/div/div[2]/div[1]/input").send_keys(getUsername(directory, 'Loot TV'))
    #enter password
    driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div[2]/div/div/div[2]/div[2]/input").send_keys(getPassword(directory, 'Loot TV'))
    # click sign in
    driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div[2]/div/div/div[3]/button").click()
    # click to watch video
    driver.find_element(By.XPATH, "//*[@id='__next']/div/div[2]/div[2]/div/div/div/div[3]/div/div[1]/div[2]/div[2]/div[1]/p").click()

def ptcAds(directory, driver):
    view_length = ""
    selection = ""
    still_ads = True

    driver.get("https://cointiply.com/ptc")
    time.sleep(1)
    main_window = driver.window_handles[0]
    while still_ads:
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
            driver.close()
        driver.switch_to.window(main_window)
        # make sure there are coins to be earned
        avail_coins = driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[1]/div/div[1]/div[2]").text
        if int(avail_coins[0]) > 0:
            try:
                # click to enable Rain Pool button
                driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[1]/div[4]/div[2]/div/div[2]/span[3]").click()
                time.sleep(1)
                # "Click to qualify for rain pool
                driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[1]/div[4]/div[2]/div/div[2]/div/label[2]").click()
                time.sleep(1)
                # click I UNDERSTAND
                try:
                    driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[3]/button[2]").click()
                except NoSuchElementException:
                    driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/div[3]/button[2]").click()
            except (ElementNotInteractableException, ElementClickInterceptedException):
                exception = "already registered"
            time.sleep(1)
            try:
                # click on view highest paying add link
                driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[1]/div/div[1]/div[3]/button").click()
                time.sleep(1)
                # Obtain how long ad needs to be viewed for
                driver.switch_to.window(main_window)
                # Capture "X seconds remaining" element text
                view_length = driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/span").text
            except (NoSuchElementException, StaleElementReferenceException):
                print('view length not found')
                continue

            ## register ad viewing
            try:
                window_after = driver.window_handles[1]
                driver.switch_to.window(window_after)
            except IndexError: # list index out of range
                # skip ad
                driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div/div[2]/div[2]/div/div/div[2]/button").click()
                driver.refresh()
                continue
            time.sleep(1)
            driver.switch_to.window(main_window)
            current_pos = pyautogui.position()
            # click on screen, move back to current_pos
            pyautogui.leftClick(1150, 250)
            pyautogui.moveTo(current_pos)
            driver.switch_to.window(window_after)
            try:
                view_length = int(view_length[0] + view_length[1]) + 3
                time.sleep(view_length)
            except ValueError:
                print('error')
                driver.switch_to.window(main_window)
                driver.refresh()
                continue

            viewComplete = False
            while not(viewComplete):
                driver.switch_to.window(main_window)
                time.sleep(1)
                if "Ad View Complete" in driver.title:
                    viewComplete = True
                else:
                    secondsLeft = int(driver.title.replace(" Seconds Left (Viewing Ad)", ""))
                    driver.switch_to.window(window_after)
                    time.sleep(secondsLeft + 2)
            # obtain which image needs to be selected
            try:
                selection = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/span[1]").text.replace("Select: ", "")
            except NoSuchElementException:
                try:
                    # skip ad
                    showMessage('unable to find selection', 'clicking OK will skip ad')
                    print('skipped ad')
                    driver.find_element(By.ID, "//*[@id='app']/div[4]/div/div/div[2]/div[1]/div/div[2]/div/div/div[2]/button").click()
                    driver.refresh()
                    time.sleep(2)
                    continue
                except NoSuchElementException:
                    continue
            time.sleep(1)
            # take screenshot of captcha images
            myScreenshot = pyautogui.screenshot(region=(650, 400, 600, 400))
            myScreenshot.save(directory + r"\Projects\Coding\Python\MRAutomation\Resources\captcha images\captcha_shot.png")
            template = ''
            template = cv2.imread(directory + r"\Projects\Coding\Python\MRAutomation\Resources\captcha images" + '\\' + selection + '.png')
            if not isinstance(template,np.ndarray):
                showMessage("check captcha", f'selection: {selection}  not available')
                continue
            
            img = cv2.imread(directory + r"\Projects\Coding\Python\MRAutomation\Resources\captcha images\captcha_shot.png")
            img2 = img.copy()
            w, h = template.shape[:-1]
            methods = ['cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF_NORMED']
            x_coord = 0
            for i in methods:
                img = img2.copy()
                method = eval(i)
                res = cv2.matchTemplate(img, template, method)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                top_left = min_loc if method in [cv2.TM_SQDIFF_NORMED] else max_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                cv2.rectangle(img, top_left, bottom_right, 255, 2)
                x_coord = x_coord + int(top_left[0])
                # removes the code to draw rectangle (keeping for troubleshooting reference)
                # plt.subplot(121), plt.imshow(res, cmap='gray')
                # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
                # plt.subplot(122), plt.imshow(img, cmap='gray')
                # plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
                # plt.suptitle(i)
                # plt.show()
            x_coord_avg = x_coord / 2
            time.sleep(1)
            img_num = 0
            if x_coord_avg < 107:
                img_num = 1
            elif 107 <= x_coord_avg <= 200:
                img_num = 2
            elif 200 <= x_coord_avg <= 300:
                img_num = 3
            elif 300 <= x_coord_avg <= 400:
                img_num = 4
            elif x_coord_avg > 400:
                img_num = 5
            driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div[1]/img[" + str(img_num) + "]").click()
            time.sleep(1)
        else:
            still_ads = False


def nextRun(driver):
    minsLeftForFaucet = 60
    if runFaucet:
        # Get Faucet Wait Time
        driver.get("https://cointiply.com/home?intent=faucet")
        time.sleep(2)
        try: 
            minsLeftForFaucet = int(driver.find_element(By.XPATH, "/html/body/div/div/div[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/ul/li[3]/p[1]").text) + 1
        except NoSuchElementException:
            try:
                driver.find_element(By.XPATH, "//*[@id='app']/div[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/div/button")
                exception = "faucet wasn't run"
            except NoSuchElementException:
                print('time left not accurately captured, check web element')
    return minsLeftForFaucet


def runCointiply(directory, driver, faucetRun=True):
    cointiplyLogin(directory, driver)    
    runFaucet(driver, faucetRun)
    ptcAds(directory, driver)
    return nextRun(driver)


if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(2)
    runCointiply(directory, driver, True)
