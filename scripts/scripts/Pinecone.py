import time

if __name__ == '__main__' or __name__ == "Pinecone":
    from Classes.Asset import Security
    from Classes.Selenium import WebDriver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import getPassword

else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import getPassword


def locatePineconeWindow(driver):
    found = driver.findWindowByUrl("pineconeresearch.com")
    if not found:   pineConeLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)    
    
def pineConeLogin(driver):
    driver.openNewWindow('https://www.pineconeresearch.com/#/login')
    driver.getElementAndClick('xpath', "//*[@id='desktop-header-signin']/span[1]/span") # Sign In
    # driver.getElementAndSendKeys('id', "password-1", getPassword('PineCone Research')) # enter password
    time.sleep(2)
    driver.getElementAndClick('id', "sign-in-modal-submit-btn") # Sign In

def getPineConeBalance(driver):
    locatePineconeWindow(driver)    
    rawBalance = driver.getElementText('xpath', "/html/body/app-root/div/lib-main-template/lib-header/header/lib-banner/div/div/lib-banner-rewards/a/span")
    if rawBalance:
        balance = float(rawBalance.replace('Rewards Balance: ', '').replace(' Points', ''))
        return balance
    else:
        print("Could not find PineCone balance on page, could be login error or not finding balance element.")
        return False
    
def claimPineConeRewards(driver):
    locatePineconeWindow(driver)    
    driver.webDriver.get("https://www.pineconeresearch.com/redeem")
    driver.getElementAndClick('id', "redeemRewardsSelect-0")  # Redeem Rewards
    driver.getElementAndClick('xpath', "//*[@id='redeemRewardsSelect-0']/option[2]") # Redeem 1000 points
    driver.getElementAndClick('xpath', "  //*[@id='content']/lib-page/div/lib-hero-rewards/section/div/div/div[2]/div/div/div[2]/div/form/button/span[1]/span") # Redeem Now
    driver.getElementAndSendKeys('id', "password-0", getPassword('PineCone Research')) # enter password
    driver.getElementAndClick('id', "confirm-password-submit")  # Sign In

def runPinecone(driver, account, book):
    locatePineconeWindow(driver)
    account.setBalance(getPineConeBalance(driver))
    book.updateMRBalance(account, 'Surveys')
    # if float(account.balance) >= 1000:   claimPineConeRewards(driver)

if __name__ == '__main__':
    driver = WebDriver("Chrome")
    book = GnuCash('Finance')
    Pinecone = Security("Pinecone", book)
    runPinecone(driver, Pinecone, book)
    book.closeBook()

