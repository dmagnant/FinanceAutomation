import time

from selenium.webdriver.common.keys import Keys

if __name__ == '__main__' or __name__ == "Tellwut":
    from Classes.WebDriver import Driver
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, getLogger
    from Classes.WebDriverContext import WebDriverContext
else:
    from .Functions.GeneralFunctions import showMessage, getLogger
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Classes.WebDriver import Driver
    from .Classes.WebDriverContext import WebDriverContext
    
def locateTellWutWindow(driver):
    found = driver.findWindowByUrl("tellwut.com")
    if not found:   tellwutLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)
    return True

def tellwutLogin(driver):
    driver.openNewWindow('https://www.tellwut.com/')
    driver.getElementAndClick('xpath', '/html/body/main/header/div[4]/button', wait=2) # LOGIN button           
    time.sleep(1)
    driver.getElementAndClick('xpath', "/html/body/div[1]/div/div/div/div[2]/form/button", wait=1) # LOGIN button (again)
        
def getTellWutBalance(driver):
    locateTellWutWindow(driver)
    return driver.getElementText('xpath', "/html/body/main/header/div[4]/a/div/div[2]/span", allowFail=False)

def clickButtons(driver, type): # click all checkboxes
    if type == 'radio' or type == 'checkbox':
        path = "//input[@type='" + type + "']"
    else:
        path =  "//input"
    buttons = driver.getElements('xpath', path)
    if buttons:
        for i in buttons:
            if driver.locateElementOnPage(i):
                driver.sendKeysToElement(i, f'{type} button', Keys.SPACE)
        return True
    else:
        return False

def findSubmitButton(driver):   
    return driver.getElement('id', 'survey_form_submit', wait=2)
    
def completeTellWutSurveys(driver):
    locateTellWutWindow(driver)
    driver.webDriver.get('https://www.tellwut.com/most_recent_surveys') # load most recent surveys page
    time.sleep(2)
    if not driver.getElementAndClick('xpath', "//*[@id='surveyList']/div[1]/div[2]/div[1]/a"): # survey link
        return False
    while True:
        radio = clickButtons(driver, 'radio')
        checkbox = clickButtons(driver, 'checkbox')
        if not (radio or checkbox):
            print('no questions found to answer on survey load, exiting')
            break # no questions found to answer, exiting
        while True:
            if not driver.getElementAndSendKeys('id', 'survey_form_submit', Keys.ENTER, wait=2): # Click Submit
                print('no submit button found')
                if driver.getElementLocateAndClick('xpath', f"//button[@class='btn btn-primary pm-btn nextQuestion nextQuestionPagebreak']", wait=2): # Next
                    print('clicked Next')
                    if not (clickButtons(driver, 'all')):
                        print('no questions found to answer after clicking next, exiting')
                        break
                else:
                    break
            else:
                break
        time.sleep(1)
        driver.getElementLocateAndClick('partial_link_text', "NEXT POLL", wait=5) # NEXT POLL
    return True
        
def redeemTellWutRewards(driver, account):
    if int(account.balance) < 11000:    
        print("Insufficient funds to redeem TellWut rewards")
        return False
    locateTellWutWindow(driver)
    driver.webDriver.get("https://www.tellwut.com/product/144--25-PayPal.html")
    checkout = driver.getElementAndClick('id', "checkout_form_submit")
    formButton = driver.getElementAndClick('id', "form_button")
    accept = driver.getElementAndClick('id', "accept-additional")
    if not (checkout and formButton and accept):
        print("FAILED TO REDEEM TELLWUT REWARDS")

def runTellwut(driver, account, book, log=getLogger()):
    locateTellWutWindow(driver)
    completeTellWutSurveys(driver)
    account.setBalance(getTellWutBalance(driver))
    book.updateMRBalance(account)
    redeemTellWutRewards(driver, account)
    return True

if __name__ == '__main__':
    driver = Driver("Chrome")
    book = GnuCash('Finance')
    Tellwut = Security("Tellwut", book)
    runTellwut(driver, Tellwut, book)
    book.closeBook()
                                 
                                 
