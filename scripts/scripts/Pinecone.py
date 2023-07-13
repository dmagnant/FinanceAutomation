import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException


if __name__ == '__main__' or __name__ == "Pinecone":
    from Classes.Asset import Security
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
else:
    from .Classes.Asset import Security
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash

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
    loading = True
    while loading:
        try:
            driver.find_element(By.ID, "3").click() # Redeem
            loading = False
        except ElementClickInterceptedException:
            exception = "still Loading"
    time.sleep(3)
    driver.get("https://rewards.pineconeresearch.com/shop/wishlist/")
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[1]/span[1]/a").click()  # link for product
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/div[2]/form/div/div[2]/input").click()  # add to cart
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[4]/div[1]/div/div[2]/div/div/table/tbody/tr[5]/td/a").click() # checkout
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/form/div[2]/div/button").click() # Review Order
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div[3]/div/table/tbody/tr[5]/td/form/button").click() # Place Order

def runPinecone(driver, account, book):
    locatePineconeWindow(driver)
    account.setBalance(getPineConeBalance(driver))
    book.updateMRBalance(account)
    if float(account.balance) >= 300:
        claimPineConeRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Pinecone = Security("Pinecone", book)
    # runPinecone(driver, Pinecone, book)
    Pinecone.getData()
    # book.closeBook()
    # print(type(Pinecone.gnuBalance))
    # print(type(Pinecone.price))
