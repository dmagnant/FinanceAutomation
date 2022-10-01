from cProfile import run
import time

from random_words import RandomWords
from selenium.common.exceptions import WebDriverException
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

if __name__ == '__main__' or __name__ == "Presearch":
    from Functions.GeneralFunctions import setDirectory, showMessage, getCryptocurrencyPrice
    from Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash
    from Functions.SpreadsheetFunctions import updateSpreadsheet
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import setDirectory, showMessage, getCryptocurrencyPrice
    from .Functions.GnuCashFunctions import updateCoinQuantityFromStakingInGnuCash, updateCryptoPriceInGnucash
    from .Functions.SpreadsheetFunctions import updateSpreadsheet
    from .Functions.WebDriverFunctions import findWindowByUrl


def presearchLogin(driver):
    driver.execute_script("window.open('https://presearch.com/');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])

def searchUsingPresearch(driver):
    found = findWindowByUrl(driver, "presearch.com")
    if not found:
        presearchLogin(driver)
    else:
        driver.switch_to.window(found)
        time.sleep(1)    
    search_prefix = "https://presearch.com/search?q="
    search_term = None
    while search_term is None:
        search_term = RandomWords().random_word()
    time.sleep(1)
    search_path = search_prefix + search_term
    try:
        driver.get(search_path)
    except WebDriverException:
        showMessage('check issue', f'target frame detached error when trying to attempt {search_path}')
    time.sleep(1)

def claimPresearchRewards(driver):
    driver.execute_script("window.open('https://nodes.presearch.org/dashboard');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    try:
        availToStake = float(driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
    except NoSuchElementException:
        showMessage('Presearch fail', 'Check Presearch. May need to login or check element. Click OK once logged in to continue')
        driver.get("https://nodes.presearch.org/dashboard")
        availToStake = float(driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
    # claim rewards
    unclaimed = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[2]/div[3]/div[2]/div/div/div[1]/h2').text.strip(' PRE')
    if float(unclaimed) > 0:
        # click Claim
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[2]/div[3]/div[2]/div/div/div[2]/div/a').click()
        # click Claim Reward
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div/div[2]/div/form/div/button').click()
        time.sleep(4)
        driver.refresh()
        time.sleep(1)
        availToStake = float(driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[2]/div/h2').text.strip(' PRE'))
    
    # stake available PRE to highest rated node
    time.sleep(2)
    if availToStake:
        # get reliability scores
        num = 1
        node_found = False
        while not node_found:
            name = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[6]/div/table/tbody/tr[' + str(num) + ']/td[1]').text
            if name.lower() == 'aws':
                stakeAmount = availToStake
                # click Stake button
                driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[6]/div/table/tbody/tr[' + str(num) + ']/td[12]/a[1]').click()
                while stakeAmount > 0:
                    driver.find_element(By.ID, 'stake_amount').send_keys(Keys.ARROW_UP)
                    stakeAmount -= 1
                # click Update
                driver.find_element(By.XPATH, "//*[@id='editNodeForm']/div[8]/button").click()
                time.sleep(1)
                try:
                    #click Continue
                    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/div/div[2]/div[2]").click()
                    time.sleep(2)
                except NoSuchElementException:
                    exception = "No Continue button, minimum PRE met"
                driver.get('https://nodes.presearch.org/dashboard')
                node_found = True
            num += 1

def getPresearchBalance(driver):
    found = findWindowByUrl(driver, "presearch.com/dashboard")
    if not found:
        driver.execute_script("window.open('https://nodes.presearch.org/dashboard');")
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    else:
        driver.switch_to.window(found)
        time.sleep(1)
    searchRewards = float(driver.find_element(By.XPATH, '/html/body/div[1]/header/div[2]/div[2]/div/div[1]/div/div[1]/div/span[1]').text.strip(' PRE'))
    stakedTokens = float(driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/div[1]/div[2]/div/div[1]/div/h2').text.strip(' PRE').replace(',', ''))
    preTotal = searchRewards + stakedTokens
    return [preTotal, stakedTokens]

def presearchRewardsRedemptionAndBalanceUpdates(driver):
    directory = setDirectory()
    driver.implicitly_wait(5)
    claimPresearchRewards(driver)
    balances = getPresearchBalance(driver)
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'PRE', 1, balances[0], "PRE")
    updateCoinQuantityFromStakingInGnuCash(balances[0], 'PRE')
    prePrice = getCryptocurrencyPrice('presearch')['presearch']['usd']
    updateSpreadsheet(directory, 'Asset Allocation', 'Cryptocurrency', 'PRE', 2, prePrice, "PRE")
    updateCryptoPriceInGnucash('PRE', format(prePrice, ".2f"))        
    
if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    presearchLogin(driver)
    searchUsingPresearch(driver)
    response = presearchRewardsRedemptionAndBalanceUpdates(driver)
    print('balance: ' + str(response[0]))
    presearchRewardsRedemptionAndBalanceUpdates(driver, "text")
    