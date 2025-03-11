import subprocess
import time
import os

from scripts.scripts.Classes.WebDriver import Driver
from scripts.scripts.Classes.WebDriverContext import WebDriverContext
from scripts.scripts.Functions.GeneralFunctions import setDirectory
from selenium.common.exceptions import WebDriverException

# Start Chrome with remote debugging
subprocess.Popen('chrome.exe --remote-debugging-port=9223', cwd='C:\\Program Files\\Google\\Chrome\\Application', shell=True)

# Initialize the WebDriver with the session ID if it exists
driver = Driver("Chrome")
time.sleep(6)

# Attempt to load the page until successful
while True:
    try:
        driver.webDriver.get("http://127.0.0.1:8000/")
        break
    except WebDriverException:
        print("...")
        time.sleep(2)