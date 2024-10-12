import os, shutil, time, zipfile, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (InvalidArgumentException,
                                        WebDriverException, TimeoutException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if __name__ == "Classes.WebDriver":             from Functions.GeneralFunctions import setDirectory
elif __name__ == 'scripts.Classes.WebDriver':   from scripts.Functions.GeneralFunctions import setDirectory
else:                                           from scripts.scripts.Functions.GeneralFunctions import setDirectory

def configureDriverOptions(browser, asUser=True):
    if browser == "Edge":
        options = webdriver.EdgeOptions()
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("debuggerAddress","localhost:9222")
        # options.add_experimental_option("detach", True)
        profile = {"download.prompt_for_download": False}
        # options.add_experimental_option("prefs", profile)
        options.add_argument("--no-sandbox")
        if asUser:  options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
    else:        
        options = webdriver.ChromeOptions()
        # options.add_argument("enable-automation")
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--dns-prefetch-disable")
        # options.add_argument("--disable-gpu")
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
        # versionBinaryPathText = " with binary path C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        return webdriver.Edge(service=Service(directory + r"\Projects\Coding\webdrivers\msedgedriver.exe"), options=options)
    # elif browser == "Chrome":
        # versionBinaryPathText = " with binary path C:\Program Files\Google\Chrome\Application\chrome.exe"
        # if asUser:
            # from selenium import webdriver
            # from selenium.webdriver.chrome.service import Service as ChromeService
            # from webdriver_manager.chrome import ChromeDriverManager
            # driver = webdriver.Chrome(service=Service(directory + r"\Projects\Coding\webdrivers\chromedriver.exe", service_args=["--verbose", "--log-path=C:\\Users\\dmagn\\driver.txt"]), options=options)
            # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install(),service_args=["--verbose", "--log-path=C:\\Users\\dmagn\\driver1.txt"]), options=options)
    return webdriver.Chrome(service=Service(r"G:\My Drive\Projects\Coding\webdrivers\chromedriver.exe"), options=options)

class Driver:
    "this is a class for creating webdriver with implicit wait"
    def __init__(self, browser, asUser=True):
        self.webDriver = openWebDriver(browser, asUser)
        self.webDriver.implicitly_wait(5)
        
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
            self.webDriver.switch_to.window(self.webDriver.window_handles[index])
            for url in urls:
                if url in self.webDriver.current_url:   found = True
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

    def clickXPATHElementOnceAvailable(self, xpath, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.XPATH,xpath)))
            time.sleep(1)
            element.click()
            time.sleep(1)
        except TimeoutException: return False
        
    def clickIDElementOnceAvailable(self, id, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.ID,id)))
            element.click()
            time.sleep(1)
        except TimeoutException: return False
    
    def getXPATHElementOnceAvailable(self, xpath, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.XPATH,xpath)))
            return element
        except TimeoutException: return False

    def getIDElementOnceAvailable(self, id, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.ID,id)))
            return element
        except TimeoutException: return False


    def getXPATHElementTextOnceAvailable(self, xpath, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.XPATH,xpath)))
            return element.text
        except TimeoutException: return False

    def getIDElementTextOnceAvailable(self, id, wait=10):
        try:
            element = WebDriverWait(self.webDriver, wait).until(EC.element_to_be_clickable((By.ID,id)))
            return element.text
        except TimeoutException: return False