import os, shutil, time, zipfile, sys, enum, random, subprocess
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

# # Start Chrome with remote debugging
# subprocess.Popen(
#     r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="G:\My Drive\Projects\Coding\customChromeUser\User Data" --disable-gpu --log-level=3',
#     shell=True
# )

# subprocess.Popen('python manage.py runserver', cwd='G:\\My Drive\\Projects\\Coding\\Python\\FinanceAutomation', shell=True)


options = webdriver.ChromeOptions()
# options.set_capability("pageLoadStrategy", "eager")
# options.set_capability("timeouts", {"implicit":1000})
options.add_argument("start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")
options.add_argument(r"--user-data-dir=G:\My Drive\Projects\Coding\customChromeUser\User Data")
print('got here')
options.debugger_address="localhost:9223"


driver = webdriver.Chrome(service=Service(r"G:\My Drive\Projects\Coding\webdrivers\chromedriver.exe"), options=options)
driver.get("https://google.com")
time.sleep(5)
driver.quit()
