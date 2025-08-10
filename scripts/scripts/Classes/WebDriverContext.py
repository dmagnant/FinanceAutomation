# import os
# import tempfile
# from selenium import webdriver
# from selenium.common.exceptions import WebDriverException, NoSuchWindowException, JavascriptException, ElementNotInteractableException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver import ActionChains
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# if __name__ == "Classes.WebDriverContext":              
#     from Functions.GeneralFunctions import setDirectory, getLogger
# elif __name__ == 'scripts.Classes.WebDriverContext':    
#     from scripts.Functions.GeneralFunctions import setDirectory, getLogger
# else:                                                   
#     from scripts.scripts.Functions.GeneralFunctions import setDirectory, getLogger

# def configureDriverOptions(browser, asUser=True):
#     if browser == "Edge":
#         options = webdriver.EdgeOptions()
#         options.add_experimental_option("debuggerAddress", "localhost:9222")
#         options.add_argument("--no-sandbox")
#         if asUser:  
#             options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
#     else:        
#         options = webdriver.ChromeOptions()
#         options.debugger_address = "localhost:9223"
#     if browser == "Chrome":
#         options.set_capability("pageLoadStrategy", "eager")
#         options.set_capability("timeouts", {"implicit": 1000})
#         if asUser:  
#             user_data_dir = tempfile.mkdtemp()
#             options.add_argument(f"user-data-dir={user_data_dir}")
#     elif browser == "Brave":
#         options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
#         if asUser:  
#             user_data_dir = tempfile.mkdtemp()
#             options.add_argument(f"user-data-dir={user_data_dir}")
#     options.add_argument("start-maximized")
#     return options

# def openWebDriver(browser, asUser=True):
#     directory = setDirectory()
#     options = configureDriverOptions(browser, asUser)
#     if browser == "Edge":
#         return webdriver.Edge(service=Service(directory + r"\Projects\Coding\webdrivers\msedgedriver.exe"), options=options)
#     return webdriver.Chrome(service=Service(r"G:\My Drive\Projects\Coding\webdrivers\chromedriver.exe"), options=options, keep_alive=False)

# class WebDriverContext:
#     _instance = None

#     def __new__(cls, browser="Chrome", asUser=True):
#         if cls._instance is None:
#             cls._instance = super(WebDriverContext, cls).__new__(cls)
#             cls._instance.browser = browser
#             cls._instance.asUser = asUser
#             cls._instance.webDriver = None
#             cls._instance.log = getLogger()
#         return cls._instance

#     def __enter__(self):
#         if self.webDriver is None:
#             self.webDriver = self._initialize_driver()
#             self.webDriver.implicitly_wait(2)
#             self.webDriver.set_page_load_timeout(5)
#         return self

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.webDriver:
#             self.webDriver.quit()
#             self.webDriver = None

#     def _initialize_driver(self):
#         return openWebDriver(self.browser, self.asUser)

#     def checkWebDriverStatus(self):
#         try:
#             self.webDriver.current_url
#             return True
#         except (WebDriverException, NoSuchWindowException):
#             return False

#     def findWindowByUrl(self, url):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         currentWindow = self.webDriver.current_window_handle
#         if url in self.webDriver.current_url:   
#             return currentWindow
#         if len(self.webDriver.window_handles) > 1:
#             for i in self.webDriver.window_handles:
#                 self.webDriver.switch_to.window(i)
#                 if url in self.webDriver.current_url:   
#                     return self.webDriver.current_window_handle
#         self.webDriver.switch_to.window(currentWindow)
#         return False

#     def closeWindowsExcept(self, urls, displayWindowHandle=''):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         index = 0
#         for window in self.webDriver.window_handles:
#             found = False
#             self.webDriver.switch_to.window(self.webDriver.window_handles[index])
#             for url in urls:
#                 if url in self.webDriver.current_url:   
#                     found = True
#             if found:   
#                 index += 1
#             else:   
#                 self.webDriver.close()
#         if displayWindowHandle: 
#             self.webDriver.switch_to.window(displayWindowHandle)
#         else:   
#             self.switchToLastWindow()
                
#     def openNewWindow(self, url):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         self.findWindowByUrl(self.webDriver.current_url)
#         self.webDriver.execute_script(f"window.open('')")
#         self.findWindowByUrl('about:blank')
#         self.webDriver.get(url)
                
#     def switchToLastWindow(self):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         self.webDriver.switch_to.window(self.webDriver.window_handles[len(self.webDriver.window_handles)-1])

#     def locateElementOnPage(self, element):
#         try:
#             ActionChains(self.webDriver).move_to_element(element).perform()
#             return element
#         except (JavascriptException, ElementNotInteractableException):
#             print('unable to locate element')
#         return False

#     def getElement(self, type, path, wait=5, allowFail=True, elementState='visible'):
#         try:
#             element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.__dict__[type.upper()], path)))
#             return element
#         except TimeoutException:
#             if not allowFail:
#                 print(f'Element not found: {path}')
#             return False
    
#     def clickElement(self, element, path):
#         try:
#             element.click()
#             return element
#         except ElementClickInterceptedException:
#             print(f'ElementClickInterceptedException: {path}')
#         except ElementNotInteractableException:
#             print(f'ElementNotInteractableException: {path}')
#         except StaleElementReferenceException:
#             print(f'StaleElementReferenceException: {path}')
#         return False
    
#     def sendKeysToElement(self, element, path, keys):
#         try:
#             element.send_keys(keys)
#             return element
#         except ElementNotInteractableException:
#             print(f'ElementNotInteractableException: {path}')
#         return False

#     def getElementAndClick(self, type, path, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element:
#             return self.clickElement(element, path)
#         else:
#             return False
        
#     def getElementText(self, type, path, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element: 
#             return element.text
#         else:       
#             return False

#     def getElementTextAndLocate(self, type, path, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element: 
#             self.locateElementOnPage(element)
#             return element.text
#         else:       
#             return False

#     def getElementLocateAndClick(self, type, path, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element: 
#             self.locateElementOnPage(element)
#             return self.clickElement(element, path)
#         else:       
#             return False

#     def getElementLocateAndSendKeys(self, type, path, keys, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element: 
#             self.locateElementOnPage(element)
#             return self.sendKeysToElement(element, path, keys)
#         else:       
#             return False

#     def getElementAndSendKeys(self, type, path, keys, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         element = self.getElement(type, path, wait, allowFail)
#         if element:
#            return self.sendKeysToElement(element, path, keys)
#         else:
#             return False

#     def getElements(self, type, path, wait=5, allowFail=True):
#         if not self.checkWebDriverStatus():
#             raise WebDriverException("WebDriver is not active or window is closed.")
#         if self.getElement(type, path, wait, allowFail):
#             return self.webDriver.find_elements(By.__dict__[type.upper()], path)
#         else:
#             return False