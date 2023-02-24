import ctypes
import os
import time
from datetime import timedelta

import psutil
import pyautogui
import pygetwindow
import pyotp
from pycoingecko import CoinGeckoAPI
from pykeepass import PyKeePass
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.common.by import By

def showMessage(header, body): 
    MessageBox = ctypes.windll.user32.MessageBoxW
    MessageBox(None, body, header, 0)
    
def setDirectory():
    return os.environ.get('StorageDirectory')    

def startExpressVPN():
    os.startfile(r'C:\Program Files (x86)\ExpressVPN\expressvpn-ui\ExpressVPN.exe')
    time.sleep(5)
    EVPN = pygetwindow.getWindowsWithTitle('ExpressVPN')[0]
    EVPN.close()  # stays open in system tray

def isProcessRunning(processName):
        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
 
def closeExpressVPN():
    if isProcessRunning('ExpressVPN.exe'):
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

def getUsername(name):
    keepass_file = setDirectory() + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).username

def getPassword(name):
    keepass_file = setDirectory() + r"\Other\KeePass.kdbx"
    KeePass = PyKeePass(keepass_file, password=os.environ.get('KeePass'))
    return KeePass.find_entries(title=name, first=True).password

def getOTP(account):
    return pyotp.TOTP(os.environ.get(account)).now()

def loginPiHole(driver):
    driver.implicitly_wait(2)
    driver.get("http://192.168.1.144/admin/")
    driver.maximize_window()
    try:
        #click Login
        driver.find_element(By.XPATH, "/html/body/div[2]/aside/section/ul/li[3]/a").click()
        # Enter Password
        driver.find_element(By.ID, "loginpw").send_keys(getPassword('Pi hole'))
        #click Login again
        driver.find_element(By.XPATH, "//*[@id='loginform']/div[2]/div/button").click()
        time.sleep(1)
    except NoSuchElementException:
        exception = "already logged in"

def disablePiHole(driver):
    driver.maximize_window()
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(driver)
    try:
        driver.find_element(By.XPATH, "//*[@id='pihole-disable']/a/span[2]").click()
        # Click Indefinitely
        driver.find_element(By.XPATH, "//*[@id='pihole-disable-indefinitely']").click()
    except ElementNotInteractableException:
        exception = "already disabled"

def enablePiHole(driver):
    pihole_window = driver.window_handles[0]
    driver.switch_to.window(pihole_window)
    loginPiHole(driver)
    try:
        driver.find_element(By.ID, "enableLabel").click()
    except NoSuchElementException:
        exception = "already enabled"
    except ElementNotInteractableException:
        exception = "already enabled"

def getStartAndEndOfDateRange(today, timeSpan):
    month = today.month
    year = today.year
    if isinstance(timeSpan, int):
        enddate = today
        startdate = (enddate - timedelta(days=timeSpan))
    else:
        if month == 1:
            startdate = today.replace(month=12, day=1, year=year - 1)
            enddate = today.replace(month=12, day=31, year=year - 1)
        elif month == 3:
            startdate = today.replace(month=2, day=1)
            enddate = today.replace(month=2, day=28)
        elif month in [5, 7, 10, 12]:
            startdate = today.replace(month=month - 1, day=1)
            enddate = today.replace(month=month - 1, day=30)
        else:
            startdate = today.replace(month=month - 1, day=1)
            enddate = today.replace(month=month - 1, day=31)
        if timeSpan == "YTD":
            startdate = startdate.replace(month=1, day=1)
    return [startdate, enddate]

def getCryptocurrencyPrice(coinList):
    return CoinGeckoAPI().get_price(ids=coinList, vs_currencies='usd')
     
def getStockPrice(driver, symbol):
    driver.openNewWindow('https://finance.yahoo.com/quote/' + symbol + "/")
    try:
        driver.webDriver.find_element(By.XPATH,"//*[@id='myLightboxContainer']/section/button[1]/svg").click()
    except NoSuchElementException:
        exception = 'pop-up window not there'
    return driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div/fin-streamer[1]").text.replace('$', '')
