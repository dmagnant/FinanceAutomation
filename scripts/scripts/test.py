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
from Classes.WebDriver import Driver


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=C:\Users\dmagn\AppData\Local\Google\Chrome\User Data")
    options.debugger_address="localhost:9223"
    driver = webdriver.Chrome(service=Service(r"G:\My Drive\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
    driver.implicitly_wait(2)
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)
    input("Press Enter to close the browser...")