import ctypes
import os
import shutil
import sys
import time
from datetime import datetime
import zipfile

import piecash
import psutil
import pyautogui
import pygetwindow
from piecash import GnucashException
from pykeepass import PyKeePass
from selenium import webdriver
from selenium.common.exceptions import (InvalidArgumentException,
                                        NoSuchElementException,
                                        SessionNotCreatedException, ElementNotInteractableException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def showMessage(header, body): 
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, body, header, 0)

def checkIfProcessRunning(processName):
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def startExpressVPN():
    os.startfile(r'C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe')
    time.sleep(5)
    EVPN = pygetwindow.getWindowsWithTitle('ExpressVPN')[0]
    EVPN.close()  # stays open in system tray

def closeExpressVPN():
    if checkIfProcessRunning('ExpressVPN.exe'):
        os.startfile(r'C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe')
        time.sleep(3)
        EVPN = pygetwindow.getWindowsWithTitle('ExpressVPN')[0]
        EVPN.restore()
        EVPN.move(0, 0)
        EVPN.activate()
        pyautogui.leftClick(40, 50)
        time.sleep(1)
        pyautogui.leftClick(40, 280)
        time.sleep(4)

def setDirectory():
    return os.environ.get('StorageDirectory')
    
def configureDriverOptions(browser, asUser=True):
    if browser == "Edge":
        options = webdriver.EdgeOptions()
        # following options not compatible to Chrome remote debugging window
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("detach", True)
        profile = {"download.prompt_for_download": False}
        options.add_experimental_option("prefs", profile)
        # if asUser:
        #     options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Microsoft\Edge\User Data")
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
        zip_ref.extractall(r"G:\My Drive\Projects\Coding\webdrivers")
    driver.quit()
    os.remove(filePath)
    if browser == "Edge":
        shutil.rmtree(r"G:\My Drive\Projects\Coding\webdrivers\Driver_Notes")

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
        # except InvalidArgumentException:
        #     print('user profile already in use, opening blank window')
        #     options = configureDriverOptions(browser, False)
        except SessionNotCreatedException:
            error = str(sys.exc_info()[1]).partition('\n')[2].partition('\n')[0]
            version = error.replace("Current browser version is ", '').replace(versionBinaryPathText, '')
            updateWebDriver(browser, version)

def findWindow(driver, title):
    if title in driver.title:
        return driver.current_window_handle
    if len(driver.window_handles) > 1:
        print('windows: ', len(driver.window_handles))
        for i in driver.window_handles:
            driver.switch_to.window(i)
            if title in driver.title:
                return driver.current_window_handle
    return False

def getUsername(directory, name):
    keepass_file = directory + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).username

def getPassword(directory, name):
    keepass_file = directory + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).password

def loginPiHole(directory, driver):
    driver.implicitly_wait(2)
    driver.get("http://192.168.1.144/admin/")
    driver.maximize_window()
    try:
        #click Login
        driver.find_element(By.XPATH, "/html/body/div[2]/aside/section/ul/li[3]/a").click()
        # Enter Password
        driver.find_element(By.ID, "loginpw").send_keys(getPassword(directory, 'Pi hole'))
        #click Login again
        driver.find_element(By.XPATH, "//*[@id='loginform']/div[2]/div/button").click()
        time.sleep(1)
    except NoSuchElementException:
        exception = "already logged in"

def disablePiHole(directory, driver):
    driver.maximize_window()
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(directory, driver)
    try:
        driver.find_element(By.XPATH, "//*[@id='pihole-disable']/a/span[2]").click()
        # Click Indefinitely
        driver.find_element(By.XPATH, "//*[@id='pihole-disable-indefinitely']").click()
    except ElementNotInteractableException:
        exception = "already disabled"

def enablePiHole(directory, driver):
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(directory, driver)
    try:
        driver.find_element(By.ID, "enableLabel").click()
    except NoSuchElementException:
        exception = "already enabled"
    except ElementNotInteractableException:
        exception = "already enabled"

def openGnuCashBook(directory, type, readOnly, openIfLocked):
    if type == 'Finance':
        book = directory + r"\Finances\Personal Finances\Finance.gnucash"
    elif type == 'Home':
        book = directory + r"\Stuff\Home\Finances\Home.gnucash"
    try:
        mybook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    except GnucashException:
        showMessage("Gnucash file open", 'Close Gnucash file then click OK \n')
        mybook = piecash.open_book(book, readonly=readOnly, open_if_lock=openIfLocked)
    return mybook

def calculateNextRun(minsLeftForFaucet):
    now = datetime.now().time().replace(second=0, microsecond=0)
    if now.hour == 23:
        nextRunMinute = 0
        nextRunHour = 0
    elif now.hour == 18:
        nextRunMinute = 0
        nextRunHour = 19
        minsLeftForFaucet = 61 - now.minute
    else:
        nextRunMinute = now.minute + minsLeftForFaucet
        nextRunHour = now.hour
        if (nextRunMinute >= 60):
            nextRunMinute = abs(nextRunMinute - 60)
            nextRunHour += 1 if nextRunHour < 23 else 0
    if nextRunMinute < 0 or nextRunMinute > 59:
        showMessage('Next Run Minute is off', 'Nextrunminute = ' + str(nextRunMinute))
    nextRun = now.replace(hour=nextRunHour, minute=nextRunMinute)
    print('next run at ', str(nextRun.hour) + ":" + "{:02d}".format(nextRun.minute))
    if nextRun.hour == 0:
        minsLeftForFaucet -= datetime.now().time().minute
    time.sleep(minsLeftForFaucet * 60)
