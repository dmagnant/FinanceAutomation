import os, shutil, time, zipfile, sys, enum, random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (InvalidArgumentException,
                                        WebDriverException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException, JavascriptException, NoSuchWindowException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import ReadTimeoutError, NewConnectionError, MaxRetryError

if __name__ == "Classes.WebDriver":             from Functions.GeneralFunctions import setDirectory, showMessage
elif __name__ == 'scripts.Classes.WebDriver':   from scripts.Functions.GeneralFunctions import setDirectory, showMessage
else:                                           from scripts.scripts.Functions.GeneralFunctions import setDirectory, showMessage

class ElementTypes(enum.Enum):
    ID = id = By.ID
    XPATH = xpath = By.XPATH
    LINK_TEXT = link_text = By.LINK_TEXT
    PARTIAL_LINK_TEXT = partial_link_text = By.PARTIAL_LINK_TEXT
    NAME = name = By.NAME
    TAG_NAME = tag_name = By.TAG_NAME
    CLASS_NAME = class_name = By.CLASS_NAME
    CSS_SELECTOR = css_selector = By.CSS_SELECTOR

class ExpectedConditions(enum.Enum):
    clickable = EC.element_to_be_clickable
    visible = EC._element_if_visible

def configureDriverOptions(browser, asUser=True):
    if browser == "Edge":
        options = webdriver.EdgeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        options.add_argument("--no-sandbox")
        if asUser:  options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
    else:        
        options = webdriver.ChromeOptions()
        options.debugger_address="localhost:9223"
    if browser == "Chrome":
        options.set_capability("pageLoadStrategy", "eager")
        options.set_capability("timeouts", {"implicit":1000})
        if asUser:  
            options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Google\Chrome\User Data")
    elif browser == "Brave":
        options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        if asUser:  options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\BraveSoftware\Brave-Browser\User Data")
    options.add_argument("start-maximized")
    return options

def updateWebDriver(browser, version):
    directory = setDirectory()
    if (browser == "Chrome" or browser == "Brave"):
        url = "https://chromedriver.chromium.org/downloads"
        filePath = r"C:\Users\dmagn\Downloads\chromedriver_win32.zip"
        driver = openWebDriver("Edge", False)
        driver.implicitly_wait(5)
        driver.get(url)
        driver.find_element(By.PARTIAL_LINK_TEXT, "ChromeDriver " + version.partition('.')[0]).click()
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.find_element(By.PARTIAL_LINK_TEXT, "chromedriver_win32.zip").click()
    elif browser == "Edge":
        url = f"https://msedgedriver.azureedge.net/{version}/edgedriver_win64.zip"
        filePath = r"C:\Users\dmagn\Downloads\edgedriver_win64.zip"
        driver = openWebDriver("Chrome", False)
        driver.implicitly_wait(5)
        driver.get(url)
    time.sleep(3)
    with zipfile.ZipFile(filePath, 'r') as zip_ref: zip_ref.extractall(directory + r"\Projects\Coding\webdrivers")
    driver.quit()
    os.remove(filePath)
    if browser == "Edge":   shutil.rmtree(directory + r"\Projects\Coding\webdrivers\Driver_Notes")

def openWebDriver(browser, asUser=True):
    directory = setDirectory()
    options = configureDriverOptions(browser, asUser)
    if browser == "Edge":
        return webdriver.Edge(service=Service(directory + r"\Projects\Coding\webdrivers\msedgedriver.exe"), options=options)
    return webdriver.Chrome(service=Service(r"G:\My Drive\Projects\Coding\webdrivers\chromedriver.exe"), options=options)

class Driver:
    "this is a class for creating webdriver with implicit wait"
    def __init__(self, browser, asUser=True, session_id=None):
        self.webDriver = openWebDriver(browser, asUser)
        self.webDriver.implicitly_wait(10)  # Increase implicit wait
        # self.webDriver.set_page_load_timeout(30)  # Increase page load timeout
        # self.webDriver.set_script_timeout(30)  # Increase script timeout

    def findWindowByUrl(self, url):
        currentWindow = self.webDriver.current_window_handle
        if url in self.webDriver.current_url:   return currentWindow
        if len(self.webDriver.window_handles) > 1:
            for i in self.webDriver.window_handles:
                self.webDriver.switch_to.window(i)
                if url in self.webDriver.current_url:   
                    return self.webDriver.current_window_handle
        self.webDriver.switch_to.window(currentWindow)
        return False

    def closeWindowsExcept(self, urls, displayWindowHandle=''):
        index = 0
        for window in self.webDriver.window_handles:
            found = False
            pageUrl = ''
            self.webDriver.switch_to.window(self.webDriver.window_handles[index])
            
            try:
                pageUrl = self.webDriver.current_url
            except (ReadTimeoutError, MaxRetryError):    pass
            if pageUrl:
                for url in urls:
                    if url in pageUrl:      
                        found = True
                        break
            if found:   index += 1
            else:   self.webDriver.close()
        if displayWindowHandle: self.webDriver.switch_to.window(displayWindowHandle)
        else:   self.switchToLastWindow()
                
    def openNewWindow(self, url):
        self.findWindowByUrl(self.webDriver.current_url)
        self.webDriver.execute_script(f"window.open('')")
        self.findWindowByUrl('about:blank')
        self.webDriver.get(url)
                
    def switchToLastWindow(self):
        self.webDriver.switch_to.window(self.webDriver.window_handles[len(self.webDriver.window_handles)-1])

    def locateElementOnPage(self, element):
        try:
            ActionChains(self.webDriver).move_to_element(element).perform()
            return element
        except (JavascriptException, ElementNotInteractableException):
            print('unable to locate element')
        return False

    def getElement(self, type, path, wait=5, allowFail=True, elementState='visible'):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((ElementTypes[type].value,path)))
            return element
        except (TimeoutException, StaleElementReferenceException):
            if not allowFail:
                print(f'Element not found: {path}')
            return False
    
    def clickElement(self, element, path):
        try:
            element.click()
            return element
        except ElementClickInterceptedException:
            print(f'ElementClickInterceptedException: {path}')
        except ElementNotInteractableException:
            print(f'ElementNotInteractableException: {path}')
        except StaleElementReferenceException:
            print(f'StaleElementReferenceException: {path}')
        return False
    
    def sendKeysToElement(self, element, path, keys):
        try:
            element.send_keys(keys)
            return element
        except ElementNotInteractableException:
            print(f'ElementNotInteractableException: {path}')
        return False

    def getElementAndClick(self, type, path, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element:
            return self.clickElement(element, path)
        else:
            return False
        
    def getElementText(self, type, path, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element: return element.text
        else:       return False

    def getElementTextAndLocate(self, type, path, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element: 
            self.locateElementOnPage(element)
            return element.text
        else:       return False

    def getElementLocateAndClick(self, type, path, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element: 
            self.locateElementOnPage(element)
            return self.clickElement(element, path)
        else:       return False

    def getElementLocateAndSendKeys(self, type, path, keys, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element: 
            self.locateElementOnPage(element)
            return self.sendKeysToElement(element, path, keys)
        else:       return False

    def getElementAndSendKeys(self, type, path, keys, wait=5, allowFail=True):
        element = self.getElement(type, path, wait, allowFail)
        if element:
           return self.sendKeysToElement(element, path, keys)
        else:
            return False

    def getElements(self, type, path, wait=5, allowFail=True):
        if self.getElement(type, path, wait, allowFail):
            return self.webDriver.find_elements(ElementTypes[type].value, path)
        else:
            return False