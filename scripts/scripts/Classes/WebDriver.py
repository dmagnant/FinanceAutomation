if __name__ == "Classes.WebDriver":
    from Functions.WebDriverFunctions import openWebDriver
else:
    from scripts.scripts.Functions.WebDriverFunctions import openWebDriver

class Driver:
    "this is a class for creating webdriver with implicit wait"
    def __init__(self, browser, asUser=True):
        self.webDriver = openWebDriver(browser, asUser)
        self.webDriver.implicitly_wait(5)
