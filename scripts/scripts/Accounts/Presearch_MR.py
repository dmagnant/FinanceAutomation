import time

from random_words import RandomWords
from selenium.common.exceptions import WebDriverException
import sys
sys.path.append("..")
from ..Functions import openWebDriver, showMessage

def runPresearch(driver):
    search_prefix = "https://presearch.com/search?q="
    search_term = None
    while search_term is None:
        search_term = RandomWords().random_word()
    time.sleep(1)
    search_path = search_prefix + search_term
    try:
        driver.get(search_path)
    except WebDriverException:
        showMessage('check issue', f'target frame detached error when trying to attempt {search_path}')
    time.sleep(1)

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    runPresearch(driver)
