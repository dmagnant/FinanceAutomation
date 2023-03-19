import time

from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Pinecone":
    from Classes.WebDriver import Driver
if __name__ == '__main__' or __name__ == "Pinecone":
    from Classes.Asset import Crypto
    from Classes.WebDriver import Driver
    from Functions.GnuCashFunctions import openGnuCashBook
else:
    from .Classes.Asset import Crypto
    from .Classes.WebDriver import Driver
    from .Functions.GnuCashFunctions import openGnuCashBook    

def locatePineconeWindow(driver):
    found = driver.findWindowByUrl("members.pineconeresearch.com")
    if not found:
        pineConeLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)    
    
def pineConeLogin(driver):
    driver.openNewWindow('https://members.pineconeresearch.com/#/Login')
    time.sleep(4)
    # click login
    driver.webDriver.find_element(By.XPATH, "//*[@id='mainContainer']/div/div/div[1]/div/form/button").click()
    time.sleep(4)

def getPineConeBalance(driver):
    locatePineconeWindow(driver)    
    balance = ''
    while balance == '':
        balance = driver.webDriver.find_element(By.XPATH, "//*[@id='basic-navbar-nav']/div/form/button/div").text
    return balance
    
def claimPineConeRewards(driver):
    locatePineconeWindow(driver)    
    driver = driver.webDriver
    driver.find_element(By.ID, "3").click() # Redeem
    time.sleep(3)
    driver.get("https://rewards.pineconeresearch.com/shop/wishlist/")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[1]/span[1]/a").click()  # link for product
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/div[2]/form/div/div[2]/input").click()  # add to cart
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[4]/div[1]/div/div[2]/div/div/table/tbody/tr[5]/td/a").click() # checkout
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/form/div[2]/div/button").click() # Review Order
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div[3]/div/table/tbody/tr[5]/td/form/button").click() # Place Order

def runPinecone(driver, account):
    locatePineconeWindow(driver)
    account.setBalance(getPineConeBalance(driver))
    account.updateMRBalance(openGnuCashBook('Finance', False, False))
    if float(account.balance) >= 300:
        claimPineConeRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    Pinecone = Crypto("Pinecone")
    runPinecone(driver, Pinecone)
    Pinecone.getData()
