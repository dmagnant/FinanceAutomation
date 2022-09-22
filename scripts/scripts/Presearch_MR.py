import time

from random_words import RandomWords
from selenium.common.exceptions import WebDriverException

if __name__ == '__main__' or __name__ == "Presearch_MR":
    from Functions import openWebDriver, showMessage
else:
    from .Functions import showMessage

def runPresearch(driver):
    search_prefix = "https://presearch.com/search?q="
    search_term = None
    while search_term is None:
        search_term = RandomWords().random_word()
    time.sleep(1)
    search_path = search_prefix + search_term
    try:
        driver.execute_script("window.open('https://presearch.com/');")
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.get(search_path)
    except WebDriverException:
        showMessage('check issue', f'target frame detached error when trying to attempt {search_path}')
    time.sleep(1)

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    runPresearch(driver)
