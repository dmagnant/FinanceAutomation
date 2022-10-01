import subprocess
import time

from scripts.scripts.Functions.WebDriverFunctions import openWebDriver

subprocess.Popen('python manage.py runserver', cwd='G:\\My Drive\\Projects\\Coding\\Python\\FinanceAutomation', shell=True)
time.sleep(2)
subprocess.Popen('chrome.exe --remote-debugging-port=9222', cwd='C:\\Program Files\\Google\\Chrome\\Application', shell=True)
driver = openWebDriver("Chrome")
driver.get("http://127.0.0.1:8000/")
