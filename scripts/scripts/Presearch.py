import time
from statistics import mode
import random

from random_words import RandomWords
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Presearch":
    from Classes.Asset import Security, USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage
else:
    from .Classes.Asset import Security, USD
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage

class Node(object):
    "this is a class for tracking presearch node information"
    # def __init__(self, num, name, currentStake, reliabilityScore):
    def __init__(self, num, name, reliabilityScore):
        self.num = num
        self.name = name
        self.reliabilityScore = reliabilityScore
    
    def stakePRE(self, driver, stakeAmount):
        availToStake = float(driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
        driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(self.num) + ']/td[12]/a[1]').click() # stake button
        if availToStake < stakeAmount:
            stakeAmount = availToStake
        while stakeAmount > 0:
            driver.webDriver.find_element(By.ID, 'stake_amount').send_keys(Keys.ARROW_UP)
            stakeAmount -= 1        
        driver.webDriver.find_element(By.XPATH, "//*[@id='editNodeForm']/div[9]/button").click() # update
        time.sleep(1)
        # try:
        #     driver.webDriver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[2]").click() # continue
        #     time.sleep(2)
        # except NoSuchElementException:
        #     exception = "No Continue button, minimum PRE met"
        driver.webDriver.get('https://nodes.presearch.org/dashboard')
    
    # def checkme(self):
    #     print(str(self.num) + '\n' + self.name + '\n' + str(self.reliabilityScore))
    
def getPresearchBasePath():
    return '/html/body/div[2]/div[2]/div[5]/div[' 

def locatePresearchWindow(driver):
    found = driver.findWindowByUrl("presearch.com")
    if not found:
        presearchLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)    

def presearchLogin(driver):
    driver.openNewWindow('https://presearch.com/')

def searchUsingPresearch(driver):
    locatePresearchWindow(driver)
    num = 1
    while num < 3:
        search_prefix = "https://presearch.com/search?q="
        search_term = None
        while search_term is None:
            search_term = RandomWords().random_word()
        time.sleep(1)
        search_path = search_prefix + search_term
        try:
            driver.webDriver.get(search_path)
        except WebDriverException:
            showMessage('check issue', f'target frame detached error when trying to attempt {search_path}')
        time.sleep(random.choice([2, 3, 4]))
        num+=1

def claimPresearchRewards(driver):
    locatePresearchWindow(driver)
    driver = driver.webDriver
    driver.get("https://nodes.presearch.org/dashboard")   
    try:
        float(driver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
    except NoSuchElementException:
        showMessage('Presearch fail', 'Check Presearch. May need to login or check element. Click OK once logged in to continue')
        driver.get("https://nodes.presearch.org/dashboard")
    unclaimed = driver.find_element(By.XPATH, getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[1]/h2').text.strip(' PRE')
    if float(unclaimed) > 0:
        driver.find_element(By.XPATH, getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[2]/div/a').click() # claim
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div/div[2]/div/form/div/button').click() # claim reward
        time.sleep(4)
        driver.refresh()
        time.sleep(1)
    return float(driver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))

def stakePresearchRewards(driver, availToStake):
    locatePresearchWindow(driver)
    nodes = []
    reliabilityScores = []
    num = 1
    stillNodes = True
    while stillNodes:
        try:
            name = driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(num) + ']/td[1]').text
            reliabilityScore = driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(num) + ']/td[10]').text
            nodes.append(Node(num=num, name=name, reliabilityScore=reliabilityScore))
            reliabilityScores.append(reliabilityScore)
            num += 1
        except NoSuchElementException:
            stillNodes = False
    reliabilityScores.sort()
    rsMode = mode(reliabilityScores)
    rsMax = max(reliabilityScores)
    if rsMode == rsMax: # duplicate high scores
        count = dict((i, reliabilityScores.count(i)) for i in reliabilityScores)
        stakeAmount = availToStake / count[rsMax]
    else: # single high score
        stakeAmount = availToStake
    for n in nodes:
        if n.reliabilityScore == rsMax:
            n.stakePRE(driver, stakeAmount)

def getPresearchBalance(driver):
    found = driver.findWindowByUrl("presearch.com/dashboard")
    if not found:
        driver.openNewWindow('https://nodes.presearch.org/dashboard')
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)
    searchRewards = float(driver.webDriver.find_element(By.XPATH, '/html/body/div[1]/header/div[2]/div[2]/div/div[1]/div/div[1]/div/span[1]').text.strip(' PRE').replace(',', ''))
    stakedTokens = float(driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[1]/div/h2').text.strip(' PRE').replace(',', ''))
    balance = searchRewards + stakedTokens
    return balance

def presearchRewardsRedemptionAndBalanceUpdates(driver, account, book):
    driver.webDriver.implicitly_wait(5)
    preAvailableToStake = claimPresearchRewards(driver)
    if preAvailableToStake:
        stakePresearchRewards(driver, preAvailableToStake)
    account.setBalance(getPresearchBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)
    
if __name__ == '__main__':
    # driver = Driver("Chrome")
    book = GnuCash('Finance')
    # locatePresearchWindow(driver)
    # searchUsingPresearch(driver)
    # Presearch = Security("Presearch", book)
    # presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book)
    # Presearch.getData()
    # book.closeBook()
    
    Presearch = Security("Presearch", book)
    Presearch.getData()