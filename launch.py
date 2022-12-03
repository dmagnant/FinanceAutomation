import subprocess
import time

from scripts.scripts.Functions.WebDriverFunctions import openWebDriver
from selenium.common.exceptions import WebDriverException

subprocess.Popen('python manage.py runserver', cwd='G:\\My Drive\\Projects\\Coding\\Python\\FinanceAutomation', shell=True)
print('page will load automatically after development server starts \n')
subprocess.Popen('chrome.exe --remote-debugging-port=9222', cwd='C:\\Program Files\\Google\\Chrome\\Application', shell=True)
driver = openWebDriver("Chrome")
time.sleep(6)
while True:
    try:
        driver.get("http://127.0.0.1:8000/")
        break
    except WebDriverException:
        print("...")
        time.sleep(2)
