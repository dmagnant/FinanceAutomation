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

def getBasePaidviewpointPath():
    return '/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div[1]/div/div[1]/div/div[2]/div/div/div/div['

def getAnswerPath(num):
    return getBasePaidviewpointPath() + str(num) + "]/div/span/i"

def getDescriptionPath(num):
    return getBasePaidviewpointPath() + str(num) + ']/div/span/span'

def getAllAnswersExcept(driver, answer):
    num = 1
    stillItems = True
    while stillItems:
        try:
            description = driver.find_element(By.XPATH, getDescriptionPath(num)).text
            if description.lower() != answer.lower():
                driver.find_element(By.XPATH,getAnswerPath(num)).click()
            num += 1
        except NoSuchElementException:
            if num > 1:
                stillItems = False
            else:
                num+=1    

def getSpecificAnswer(driver, answer):
    num = 1
    found = False
    while not found:
        try:
            description = driver.find_element(By.XPATH, getDescriptionPath(num)).text
            if description.lower() == answer.lower():
                driver.find_element(By.XPATH,getAnswerPath(num)).click()
                found = True
            else:
                num+=1
        except NoSuchElementException:
            if num > 1:
                showMessage('issue with finding ' + answer + ' option', 'click ' + answer + ' manually, then click OK to proceed')
                break
            else:
                num+=1 # first option is description, not an answer option

def matchQuestionAnswer(driver, question):
    match question:
        case 'Is your career Hospitality?' | 'If you participate in this survey, you will be shown certain confidential information that is the property of a major manufacturer. This information may include, but is not limited to, experimental concepts, marketing, advertising and creative strategies and plans, and product names. In exchange for participating in this project and for the confidential information which will be shown, we ask that you agree that you will neither use nor disclose to any other person or entity any of the information provided to you in this survey.' | 'How often do you use mouthwash?' | 'Have you voted in your most recent state/local election?' | 'Were you able to successfully read all the product information?' | 'Your household income is $100,000 - $200,000.' | 'Do you own a cell/mobile phone?' | 'I agree to not discuss any information about this study. I agree that the Research Data may or may not be used in whole or in part and I assign to Researcher and its affiliates all ideas, developments, discoveries, works of authorship, designs, software, and/or inventions, whether or not patentable, conceived by me as a result of my participation in the research, and understand that Researcher may use them in any manner it sees fit.' | 'Are you currently employed?' | 'How many people report to you at your work?' | 'Do you enjoy fishing?' | 'What is your employment status?' | 'Do you purchase beer to drink at home?' | 'How much do you typically spend on groceries in a week?' | 'Have you or your partner(s) used any method of contraception in the last 12 months?' | 'You live in...':
            driver.find_element(By.XPATH,getAnswerPath(1)).click()
        case 'Which of the following best describes your role when it comes to purchasing oral care products for your household? (toothpaste, toothbrush, mouthwash, tooth whitening products, floss, etc.)' | 'What brands of mouthwash have you purchased in the past 12 months. Select all that apply.' | 'How often do you use mouthwash?' | 'How often do you exercise/work out?' | 'How many people do you live with?' | 'Do you participate in any volunteer events or activities?' | 'Do you own a pet?' | 'Have you been involved with making decisions for hospice care for a family member or friend?' | 'How many nights in the past 12 months did you stay in a hotel on a vacation?' | 'Which best describes your current relationship status?' | 'Do you personally experience hearing loss?' | 'Have often do you exercise or get outdoors?' | 'Which of the following statements best describes your involvement in decision making regarding medicines, vitamins, and supplements?' | 'What kind of video gamer are you?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
        case 'Do you consume any of the following ...':
            driver.find_element(By.XPATH,getAnswerPath(3)).click()                        
        case 'Which of the following brands of skin care products do you typically use?' | 'Who is the insurance carrier of your vehicle?':
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
        case 'Which of the following wholesale clubs do you currently belong to?' | 'How often do you watch sports either live, on TV or on a mobile device?' | 'Which, if any, of the following products do you use regularly?' | 'What type of vehicle(s) do you own?':
            driver.find_element(By.XPATH,getAnswerPath(5)).click()
        case 'Do you, or any member of your household, work for any of the following?':
            driver.find_element(By.XPATH,getAnswerPath(6)).click()
        case 'Which of the following brands of household cleaners do you typically use?' | 'Which of the following brands of health care products do you typically use?':
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
        case 'Sometimes we are looking for people who work in certain occupations. Are you, or is any member of your household, currently or formerly, employed in any of the following occupations? (Select all that apply)' | 'Which of the following best describes your current situation?' | 'Which of the following have you done to your hair in the past six months?' | 'Which of the following features does your home have for energy and/or water conservation?':
            driver.find_element(By.XPATH,getAnswerPath(8)).click()
        case 'Have you had any of the following life changing events occur in the past 12 months?':
            driver.find_element(By.XPATH,getAnswerPath(9)).click()         
        case 'Who is your cellular phone carrier(s)?':
            driver.find_element(By.XPATH,getAnswerPath(13)).click()
        case 'Which of the following describe(s) your retail shopping habits in the past 6 months?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(5)).click()
        case 'Which of the following have you purchased in the past six months?':
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
            driver.find_element(By.XPATH,getAnswerPath(5)).click()
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
        case 'Which of these items do you own?':
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
            driver.find_element(By.XPATH,getAnswerPath(9)).click()
            driver.find_element(By.XPATH,getAnswerPath(10)).click()
        case 'Which of the following types of accounts or financial products/services do you have with any bank or financial institution? Select all that apply.':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(3)).click()
            driver.find_element(By.XPATH,getAnswerPath(6)).click()
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
            driver.find_element(By.XPATH,getAnswerPath(8)).click()
            driver.find_element(By.XPATH,getAnswerPath(9)).click()
            driver.find_element(By.XPATH,getAnswerPath(10)).click()
            driver.find_element(By.XPATH,getAnswerPath(11)).click()
            driver.find_element(By.XPATH,getAnswerPath(15)).click()
            driver.find_element(By.XPATH,getAnswerPath(16)).click()
            driver.find_element(By.XPATH,getAnswerPath(22)).click()
        case 'Which of the following Social Networks do you have an account with?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(3)).click()
            driver.find_element(By.XPATH,getAnswerPath(6)).click()
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
        case 'Which smart device(s)/system(s) do you own? Please select all that apply.':
            driver.find_element(By.XPATH,getAnswerPath(7)).click()
            driver.find_element(By.XPATH,getAnswerPath(8)).click()
            driver.find_element(By.XPATH,getAnswerPath(10)).click()
        case 'What features does your residence have?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
        case 'Which of the following, if any, do you use for sending/transferring money to others?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(3)).click()            
        case 'Which of these benefits do you have at work?':
            driver.find_element(By.XPATH,getAnswerPath(2)).click()
            driver.find_element(By.XPATH,getAnswerPath(3)).click()
            driver.find_element(By.XPATH,getAnswerPath(4)).click()
        case 'How many infants under 1 year of age do you live with?':
            getSpecificAnswer(driver, '0')            
        case 'Where do you do your main grocery shopping?':
            getSpecificAnswer(driver, 'kroger')            
        case 'How often do you experience difficulty falling asleep or staying asleep?':
            getSpecificAnswer(driver, 'once a month')
        case 'Did you vote in the last U.S. presidential election?':
            getSpecificAnswer(driver, 'yes')
        case 'Which of the following have you researched or purchased in the past 6 months?' | 'Have you coped with or helped someone else cope with any of the following conditions?' | 'Which of these activities or hobbies do you enjoy?' | 'What travel services do you use frequently?' | 'Which of the following conditions do you control with diet and/or medication?' | 'Please indicate if you, or any member of your household work for any of the following: (Select all that apply)' | 'Which of the following destinations do you plan to travel to in the next 12 months?' | 'Where do you frequently purchase clothing from?':
            getSpecificAnswer(driver, 'n/a')
        case 'Do you have a land line telephone in your residence?' | 'Do you personally experience vision loss?' | 'Is your employment status Unemployed?':
            getSpecificAnswer(driver, 'no')
        case 'Do you or any member of your household work in any of the following industries?':
            getSpecificAnswer(driver, 'none of the above')
        case 'Which of these items do you regularly make purchase decisions about?' | 'Are you the primary or equal decision maker when it comes to making purchasing decisions?' | 'What types of research would you be interested in participating in?':
            getAllAnswersExcept(driver, 'n/a')
        case 'Which of the following types of products have you purchased at a retailer in the past six (6) months?':
            getAllAnswersExcept(driver, 'none of the above')
        case _:
                showMessage(f'question: {question} not found in "matchQuestionAnswer" function', 'answer question then click next')
    try:
        driver.find_element(By.ID,"link_right").click()
    except NoSuchElementException:
        exception = "button missing, etc"

def answerQuestions(driver):
    while True:
        try:
            driver.webDriver.find_element(By.XPATH,'/html/body/div[3]/div[2]/div[1]/div[2]/a') # look for survey complete
            break
        except NoSuchElementException:
            question = driver.webDriver.find_element(By.ID,"swidget-question-header-text").text
            matchQuestionAnswer(driver.webDriver, question)

def completePaidviewpointSurveys(driver):
    # while True: # option to run continuously
        locatePaidviewpointWindow(driver)
        driver.webDriver.implicitly_wait(2)
        try:
            # look for "survey available" link
            driver.webDriver.find_element(By.ID, "survey_available").click()
            print('clicked new survey')
            answerQuestions(driver)
        except ElementNotInteractableException: # survey in progress
            print('new survey not interactable')
            answerQuestions(driver)
            

        # except NoSuchElementException: # option to run continuously
        #     print('here')
        #     time.sleep(3600)

def redeemPaidviewpointRewards(driver):
    locatePaidviewpointWindow(driver)
    driver.webDriver.get('https://paidviewpoint.com/earnings')
    # click paypal
    driver.webDriver.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/div[2]/div[2]/form/div/div[1]/img').click
    # click cash out now via paypal
    driver.webDriver.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/div[2]/div[2]/form/span/span/a').click

def runPaidviewpoint(driver):
    locatePaidviewpointWindow(driver)
    completePaidviewpointSurveys(driver)
    balance = getPaidviewpointBalance(driver)
    if float(balance) >= 15:
        redeemPaidviewpointRewards(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    completePaidviewpointSurveys(driver)
    