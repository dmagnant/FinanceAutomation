import time, random
from statistics import mode

from random_word import RandomWords

from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Presearch":
    from Classes.Asset import Security, USD
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Classes.Spreadsheet import Spreadsheet
    from Functions.GeneralFunctions import showMessage
else:
    from .Classes.Asset import Security, USD
    from .Classes.GnuCash import GnuCash
    from .Classes.Spreadsheet import Spreadsheet
    from .Functions.GeneralFunctions import showMessage

class Node(object):
    "this is a class for tracking presearch node information"
    # def __init__(self, num, name, currentStake, reliabilityScore):
    def __init__(self, num, name, reliabilityScore):    self.num,self.name, self.reliabilityScore = num, name, reliabilityScore
    
    def stakePRE(self, driver, stakeAmount):
        rawStake = driver.getElementText('xpath', getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2', allowFail=False)
        if rawStake:
            availToStake = float(rawStake.replace(',','').replace(' PRE',''))
        driver.getElementAndClick('xpath', getPresearchBasePath() + '5]/div/table/tbody/tr[' + str(self.num) + ']/td[12]/a[1]') # stake button
        time.sleep(1)
        if availToStake < stakeAmount:  stakeAmount = availToStake
        while stakeAmount > 0:
            driver.getElementAndSendKeys('id', 'stake_amount', Keys.ARROW_UP)
            stakeAmount -= 1        
        driver.getElementAndClick('xpath', "//*[@id='editNodeForm']/div[9]/button") # update
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
    driver.webDriver.get("https://nodes.presearch.org/dashboard")
    unclaimedRaw = driver.getElementText('xpath', getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[1]/h2')
    if unclaimedRaw:
        unclaimed = float(unclaimedRaw.strip(' PRE'))
    else:
        showMessage('Presearch fail', 'Check Presearch. May need to login or check element. Click OK once logged in to continue')
    if unclaimed > 0:
        driver.getElementAndClick('xpath', getPresearchBasePath() + '2]/div[3]/div[2]/div/div/div[2]/div/a') # claim
        time.sleep(1)
        driver.getElementAndClick('xpath', '/html/body/div[2]/div[2]/div/div/div/div[2]/div/form/div/button') # claim reward
        time.sleep(5)
        driver.webDriver.refresh()
        time.sleep(1)
    availToStakeRaw = driver.getElementText('xpath', getPresearchBasePath() + '1]/div[2]/div/div[2]/div/h2')
    if availToStakeRaw:
        return float(availToStakeRaw.strip(' PRE'))
    else:
        return False

def stakePresearchRewards(driver, availToStake):
    print(f'avail to stake {str(availToStake)}')
    locatePresearchWindow(driver)
    num, stillNodes, nodes, reliabilityScores = 1, True, [], []
    while stillNodes:
        name = driver.getElementText('xpath', getPresearchBasePath() + '5]/div/table/tbody/tr[' + str(num) + ']/td[1]')
        if not name:
            break # no more nodes
        reliabilityScore = driver.getElementText('xpath', getPresearchBasePath() + '5]/div/table/tbody/tr[' + str(num) + ']/td[10]')
        nodes.append(Node(num=num, name=name, reliabilityScore=reliabilityScore))
        reliabilityScores.append(reliabilityScore)
        num += 1
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
    nodeStakeRaw = driver.getElementText('xpath', getPresearchBasePath() + '1]/div[2]/div/div[1]/div/h2', allowFail=False)
    if nodeStakeRaw:
        nodeStake = float(nodeStakeRaw.strip(' PRE').replace(',', ''))
    driver.webDriver.get('https://account.presearch.com/tokens/usage-rewards')
    searchStakeRaw = driver.getElementText('xpath', '/html/body/div[3]/div[3]/div[2]/div/section/dl[1]/div[1]/dd/p[1]', allowFail=False)
    if searchStakeRaw:
        searchStake = float(searchStakeRaw.strip(' PRE').replace(',', ''))    
    driver.webDriver.get('https://nodes.presearch.org/dashboard')
    if (nodeStake and searchStake):
        return searchStake + nodeStake

def presearchRewardsRedemptionAndBalanceUpdates(driver, account, book, spreadsheet):
    preAvailableToStake = claimPresearchRewards(driver)
    if preAvailableToStake: 
        stakePresearchRewards(driver, preAvailableToStake)
        account.setBalance(getPresearchBalance(driver))
        price = account.getPriceFromCoinGecko()
        price = price if price else 0.01
        account.setPrice(price)
        account.updateSpreadsheetAndGnuCash(spreadsheet, book)
    
if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Finances = Spreadsheet('Finances', 'Investments', driver)
    locatePresearchWindow(driver)
    Presearch = Security("Presearch", book)
    presearchRewardsRedemptionAndBalanceUpdates(driver, Presearch, book, Finances)
    Presearch.getData()
    book.closeBook()
