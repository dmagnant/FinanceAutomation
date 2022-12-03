
import os
import shutil
import sys
import time
import zipfile

from selenium import webdriver
from selenium.common.exceptions import (InvalidArgumentException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

if __name__ == "Classes.WebDriver":
    from Functions.GeneralFunctions import setDirectory
else:
    from scripts.scripts.Functions.GeneralFunctions import setDirectory

def configureDriverOptions(browser, asUser=True):
        if browser == "Edge":
            options = webdriver.EdgeOptions()
            # following options not compatible to Chrome remote debugging window
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("detach", True)
            profile = {"download.prompt_for_download": False}
            options.add_experimental_option("prefs", profile)
            if asUser:
                options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
        else:        
            options = webdriver.ChromeOptions()
        if browser == "Chrome":
            options.add_experimental_option("debuggerAddress","localhost:9222")
            if asUser:
                options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Google\Chrome\User Data")
        elif browser == "Brave":
            options.binary_location = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
            if asUser:
                options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\BraveSoftware\Brave-Browser\User Data")
        # applicable to all        
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
    with zipfile.ZipFile(filePath, 'r') as zip_ref:
        zip_ref.extractall(directory + r"\Projects\Coding\webdrivers")
    driver.quit()
    os.remove(filePath)
    if browser == "Edge":
        shutil.rmtree(directory + r"\Projects\Coding\webdrivers\Driver_Notes")

def openWebDriver(browser, asUser=True):
    directory = setDirectory()
    options = configureDriverOptions(browser, asUser)
    while(True):
        try:
            if browser == "Edge":
                versionBinaryPathText = " with binary path C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                return webdriver.Edge(service=Service(directory + r"\Projects\Coding\webdrivers\msedgedriver.exe"), options=options)
            elif browser == "Chrome":
                versionBinaryPathText = " with binary path C:\Program Files\Google\Chrome\Application\chrome.exe"
                return webdriver.Chrome(service=Service(directory + r"\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
            elif browser == "Brave":
                return webdriver.Chrome(service=Service(directory + r"\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
        except InvalidArgumentException:
            print('user profile already in use, opening blank window')
            options = configureDriverOptions(browser, False)
        except WebDriverException:
            print(str(sys.exc_info()[1]))
            error = str(sys.exc_info()[1]).partition('\n')[2].partition('\n')[0]
            print(error)
            version = error.replace("Current browser version is ", '').replace(versionBinaryPathText, '')
            updateWebDriver(browser, version)

class Driver:
    "this is a class for creating webdriver with implicit wait"
    def __init__(self, browser, asUser=True):
        self.webDriver = openWebDriver(browser, asUser)
        self.webDriver.implicitly_wait(5)
        
    def findWindowByUrl(self, url):
        if url in self.webDriver.current_url:
            return self.webDriver.current_window_handle
        if len(self.webDriver.window_handles) > 1:
            for i in self.webDriver.window_handles:
                self.webDriver.switch_to.window(i)
                if url in self.webDriver.current_url:
                    return self.webDriver.current_window_handle
        return False
