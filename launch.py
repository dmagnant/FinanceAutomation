import subprocess
import time
import os

from scripts.scripts.Classes.WebDriver import Driver
from scripts.scripts.Functions.GeneralFunctions import setDirectory
from selenium.common.exceptions import WebDriverException

# # Start Chrome with remote debugging
subprocess.Popen(
    r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\\Users\\dmagn\\User Data" --log-level=3',
    cwd='C:\\Program Files\\Google\\Chrome\\Application',
    shell=True
)
time.sleep(1)

# Start the Django development server
subprocess.Popen('python manage.py runserver', cwd='G:\\My Drive\\Projects\\Coding\\Python\\FinanceAutomation', shell=True)

print('page will load automatically after development server starts \n')
time.sleep(1)

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