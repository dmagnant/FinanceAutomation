import time
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Worthy":
    from Functions.GeneralFunctions import setDirectory, showMessage, getUsername, getPassword
    from Functions.WebDriverFunctions import openWebDriver, findWindowByUrl
else:
    from .Functions.GeneralFunctions import setDirectory, showMessage, getUsername, getPassword
    from .Functions.WebDriverFunctions import findWindowByUrl

def locateWorthyWindow(driver):
    found = findWindowByUrl(driver, "worthy.capital")
    if not found:
        worthyLogin(driver)
    else:
        driver.switch_to.window(found)

def worthyLogin(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://worthy.capital/start');")
    # switch to last window
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(3)
    try:
        # login
        # click Login button
        driver.find_element(By.XPATH, "//*[@id='q-app']/div/div[1]/div/div[2]/div/button[2]/span[2]/span").click()
        # enter credentials
        driver.find_element(By.ID, "1-email").send_keys(getUsername(directory, 'Worthy'))
        driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/div/div[2]/div[2]/span/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/input").send_keys(getPassword(directory, 'Worthy'))
        # click Login button (again)
        driver.find_element(By.XPATH, "//*[@id='auth0-lock-container-1']/div/div[2]/form/div/div/div/button").click()
    except NoSuchElementException:
        exception = "caught"
    time.sleep(3)


def getWorthyBalance(driver):
    locateWorthyWindow(driver)
    # Get balance from Worthy I
    worthy1BalanceElement = "//*[@id='q-app']/div/div[1]/main/div/div/div[2]/div/div[2]/div/div/div[3]/div/h4/span[3]"
    driver.find_element(By.XPATH, worthy1BalanceElement).click()
    worthy1Balance = driver.find_element(By.XPATH, worthy1BalanceElement).text.strip('$').replace(',','')
    # Get balance from Worthy II
    worthy2BalanceElement = "//*[@id='q-app']/div/div[1]/main/div/div/div[2]/div/div[3]/div/div/div[2]/div/h4/span[3]"
    driver.find_element(By.XPATH, worthy2BalanceElement).click()
    worthy2Balance = driver.find_element(By.XPATH, worthy2BalanceElement).text.strip('$').replace(',','')
    # Combine Worthy balances
    worthyTotalBalance = float(Decimal(worthy1Balance) + Decimal(worthy2Balance))
    return worthyTotalBalance

def runWorthy(driver):    
    locateWorthyWindow(driver)
    return getWorthyBalance(driver)

if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(6)
    response = runWorthy(driver)
    print(f'total balance: {response}')
    