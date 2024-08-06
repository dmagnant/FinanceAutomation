import time, random
from statistics import mode

from random_word import RandomWords
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
    def __init__(self, num, name, reliabilityScore):    self.num,self.name, self.reliabilityScore = num, name, reliabilityScore
    
    def stakePRE(self, driver, stakeAmount):
        availToStake = float(driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
        driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(self.num) + ']/td[12]/a[1]').click() # stake button
        time.sleep(1)
        if availToStake < stakeAmount:  stakeAmount = availToStake
        while stakeAmount > 0:
            driver.webDriver.find_element(By.ID, 'stake_amount').send_keys(Keys.ARROW_UP)
            stakeAmount -= 1        
        driver.webDriver.find_element(By.XPATH, "//*[@id='editNodeForm']/div[9]/button").click() # update
        time.sleep(3)
        driver.webDriver.get('https://nodes.presearch.org/dashboard')
    
def getPresearchBasePath():
    return '/html/body/div[2]/div[2]/div[5]/div[' 

def locatePresearchWindow(driver):
    found = driver.findWindowByUrl("presearch.com")
    if not found:   presearchLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)    

def presearchLogin(driver): driver.openNewWindow('https://presearch.com/')

def claimPresearchRewards(driver):
    locatePresearchWindow(driver)
    driver = driver.webDriver
    driver.get("https://nodes.presearch.org/dashboard")   
    try:    float(driver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
    except NoSuchElementException:
        showMessage('Presearch fail', 'Check Presearch. May need to login or check element. Click OK once logged in to continue')
        driver.get("https://nodes.presearch.org/dashboard")
    unclaimed = driver.find_element(By.XPATH, getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[1]/h2').text.strip(' PRE')
    if float(unclaimed) > 0:
        driver.find_element(By.XPATH, getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[2]/div/a').click() # claim
        time.sleep(1)
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div/div[2]/div/form/div/button').click() # claim reward
        time.sleep(5)
        driver.refresh()
        time.sleep(1)
    return float(driver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))

def stakePresearchRewards(driver, availToStake):
    locatePresearchWindow(driver)
    num, stillNodes, nodes, reliabilityScores = 1, True, [], []
    while stillNodes:
        try:
            name = driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(num) + ']/td[1]').text
            reliabilityScore = driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '6]/div/table/tbody/tr[' + str(num) + ']/td[10]').text
            nodes.append(Node(num=num, name=name, reliabilityScore=reliabilityScore))
            reliabilityScores.append(reliabilityScore)
            num += 1
        except NoSuchElementException:  stillNodes = False
    reliabilityScores.sort()
    rsMode = mode(reliabilityScores)
    rsMax = max(reliabilityScores)
    if rsMode == rsMax: # duplicate high scores
        count = dict((i, reliabilityScores.count(i)) for i in reliabilityScores)
        stakeAmount = availToStake / count[rsMax]
    else: stakeAmount = availToStake # single high score
    for n in nodes:
        if n.reliabilityScore == rsMax: n.stakePRE(driver, stakeAmount)

def getPresearchBalance(driver):
    found = driver.findWindowByUrl("presearch.com/dashboard")
    if not found:   driver.openNewWindow('https://nodes.presearch.org/dashboard')
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    nodeStake = float(driver.webDriver.find_element(By.XPATH, getPresearchBasePath() + '1]/div[2]/div/div[1]/div/h2').text.strip(' PRE').replace(',', ''))
    driver.webDriver.get('https://account.presearch.com/tokens/usage-rewards')
    searchStake = float(driver.webDriver.find_element(By.XPATH,'/html/body/div[3]/div[3]/div[2]/div/section/dl[1]/div[1]/dd/p[1]').text.strip(' PRE').replace(',', ''))
    driver.webDriver.get('https://nodes.presearch.org/dashboard')
    return searchStake + nodeStake

def presearchRewardsRedemptionAndBalanceUpdates(driver, account, book):
    preAvailableToStake = claimPresearchRewards(driver)
    if preAvailableToStake: stakePresearchRewards(driver, preAvailableToStake)
    account.setBalance(getPresearchBalance(driver))
    account.setPrice(account.getPriceFromCoinGecko())
    account.updateSpreadsheetAndGnuCash(book)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    locatePresearchWindow(driver)
    Presearch = Security("Presearch", book)
    presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book)
    Presearch.getData()
    book.closeBook()
    


    
    
