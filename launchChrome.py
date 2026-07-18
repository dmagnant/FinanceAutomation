import subprocess
import time
import os

from scripts.scripts.Classes.Selenium import Driver
from scripts.scripts.Functions.GeneralFunctions import setDirectory
from selenium.common.exceptions import WebDriverException

# Start Chrome with remote debugging
subprocess.Popen(
    'chrome.exe --remote-debugging-port=9223 --user-data-dir="C:\\Users\\dmagn\\User Data" --disable-gpu --log-level=3',
    cwd='C:\\Program Files\\Google\\Chrome\\Application',
    shell=True
)