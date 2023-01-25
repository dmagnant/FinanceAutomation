import time

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Paidviewpoint":
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import showMessage
else:
    from .Functions.GeneralFunctions import showMessage



def locatePaidviewpointWindow(driver):
    found = driver.findWindowByUrl("paidviewpoint.com")
    if not found:
        paidviewpointLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def paidviewpointLogin(driver):
    driver.openNewWindow('https://paidviewpoint.com/dashboard')
    script = "gotta write eventually, autologin for now"

def getPaidviewpointBalance(driver):
    locatePaidviewpointWindow(driver)
    return driver.webDriver.find_element(By.XPATH, "//*[@id='header']/div/div[1]/div[2]/div[1]/a").text.replace("$","")

def matchQuestionAnswer(driver, question):
    def getAnswerPath(num):
        return "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[" + str(num) + "]/div/span/i"
    match question:
        case 'Is your career Hospitality?' | 'If you participate in this survey, you will be shown certain confidential information that is the property of a major manufacturer. This information may include, but is not limited to, experimental concepts, marketing, advertising and creative strategies and plans, and product names. In exchange for participating in this project and for the confidential information which will be shown, we ask that you agree that you will neither use nor disclose to any other person or entity any of the information provided to you in this survey.' | 'How often do you use mouthwash?' | 'Have you voted in your most recent state/local election?' | 'Were you able to successfully read all the product information?':
            driver.find_element(By.XPATH,getAnswerPath(1)).click()
        case 'Which of the following best describes your role when it comes to purchasing oral care products for your household? (toothpaste, toothbrush, mouthwash, tooth whitening products, floss, etc.)' | 'What brands of mouthwash have you purchased in the past 12 months. Select all that apply.' | 'How often do you use mouthwash?' | 'How often do you exercise/work out?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
        case 'Which of the following wholesale clubs do you currently belong to?' | 'How often do you watch sports either live, on TV or on a mobile device?':
            driver.find_element(By.XPATH,getAnswerPath(5)).click()
        case 'Which of the following brands of household cleaners do you typically use?':
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
        case 'Sometimes we are looking for people who work in certain occupations. Are you, or is any member of your household, currently or formerly, employed in any of the following occupations? (Select all that apply)' | 'Which of the following best describes your current situation?':
            driver.find_element(By.XPATH,getAnswerPath(8)).click()
        case 'Which of these items do you own?':
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
            driver.find_element(By.XPATH,getAnswerPath(9)).click()
            driver.find_element(By.XPATH,getAnswerPath(10)).click()
        case 'Which of these items do you regularly make purchase decisions about?':
            num = 1
            stillItems = True
            while stillItems:
                try:
                    description = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div[' + str(num) + ']/div/span/span').text
                    if description.lower() != 'n/a':
                        driver.find_element(By.XPATH,getAnswerPath(num)).click()
                    num += 1
                except NoSuchElementException:
                    if num > 1:
                        stillItems = False
                    else:
                        num+=1
        case _:
                showMessage(f'question: {question} not found in "matchQuestionAnswer" function', 'answer question then click next')
    driver.find_element(By.ID,"link_right").click()

def completePaidviewpointSurveys(driver):
    
    # while True:
        locatePaidviewpointWindow(driver)
        driver.webDriver.implicitly_wait(2)
        try:
            # look for "survey available" link
            driver.webDriver.find_element(By.ID, "survey_available").click()
        except ElementNotInteractableException: # survey in progress
            # while True:
                question = driver.webDriver.find_element(By.ID,"swidget-question-header-text").text
                matchQuestionAnswer(driver.webDriver, question)

        except NoSuchElementException:
            print('here')
            time.sleep(3600)

def redeemPaidviewpointRewards(driver):
    locatePaidviewpointWindow(driver)
    script = "gotta write eventually, not enough right now"


def runPaidviewpoint(driver):
    locatePaidviewpointWindow(driver)
    completePaidviewpointSurveys(driver)
    balance = getPaidviewpointBalance(driver)
    if float(balance) >= 15:
        redeemPaidviewpointRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    completePaidviewpointSurveys(driver)
