import time

from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Pinecone":
    from Classes.WebDriver import Driver

def locatePineconeWindow(driver):
    found = driver.findWindowByUrl("members.pineconeresearch.com")
    if not found:
        pineConeLogin(driver.webDriver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)    
    
def pineConeLogin(driver):
    driver.execute_script("window.open('https://members.pineconeresearch.com/#/Login');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    time.sleep(2)
    # click login
    driver.find_element(By.XPATH, "//*[@id='mainContainer']/div/div/div[1]/div/form/button").click()
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
    # Click Redeem
    driver.find_element(By.ID, "3").click()
    time.sleep(3)
    # go to WishList
    driver.get("https://rewards.pineconeresearch.com/shop/wishlist/")
    # click link for product
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[1]/span[1]/a").click()
    # Click add to cart
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/div[2]/form/div/div[2]/input").click()
    # click checkout
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[4]/div[1]/div/div[2]/div/div/table/tbody/tr[5]/td/a").click()
    # click Review Order
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/form/div[2]/div/button").click()
    # click Place Order
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div[3]/div/table/tbody/tr[5]/td/form/button").click()

def runPinecone(driver):
    locatePineconeWindow(driver)
    balance = getPineConeBalance(driver)
    if float(balance) >= 300:
        claimPineConeRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    # runPinecone(driver)
    locatePineconeWindow(driver)