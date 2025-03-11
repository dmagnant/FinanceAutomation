import time

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
    if not found:   pineConeLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)    
    
def pineConeLogin(driver):
    driver.openNewWindow('https://members.pineconeresearch.com/#/Login')
    # time.sleep(4)
    driver.getElementAndClick('xpath', "//*[@id='mainContainer']/div/div/div[1]/div/form/button") # login
    # time.sleep(4)

def getPineConeBalance(driver):
    locatePineconeWindow(driver)    
    balance = ''
    while balance == '':
        balance = driver.getElementText('xpath', "//*[@id='basic-navbar-nav']/div/form/button/div")
    return balance
    
def claimPineConeRewards(driver):
    locatePineconeWindow(driver)    
    while True:
        if driver.getElementAndClick('id', "3"): # click Redeem
            break
    time.sleep(3)
    driver.webDriver.get("https://rewards.pineconeresearch.com/shop/wishlist/")
    driver.getElementAndClick('xpath', "/html/body/div[2]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div[2]/div[1]/span[1]/a")  # link for product
    driver.getElementAndClick('xpath', "/html/body/div[2]/div/div/div[2]/div/div[2]/div[1]/div[2]/form/div/div[2]/input")  # add to cart
    driver.getElementAndClick('xpath', "/html/body/div[2]/div/div/div[4]/div[1]/div/div[2]/div/div/table/tbody/tr[5]/td/a") # checkout
    driver.getElementAndClick('xpath', "/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/form/div[2]/div/button") # Review Order
    driver.getElementAndClick('xpath', "/html/body/div[2]/div/div/div[3]/div/div[3]/div/table/tbody/tr[5]/td/form/button") # Place Order

def runPinecone(driver, account, book):
    locatePineconeWindow(driver)
    account.setBalance(getPineConeBalance(driver))
    book.updateMRBalance(account)
    if float(account.balance) >= 1000:   claimPineConeRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Pinecone = Security("Pinecone", book)
    runPinecone(driver, Pinecone, book)
    Pinecone.getData()
    book.closeBook()
    print(type(Pinecone.gnuBalance))
    print(type(Pinecone.price))
