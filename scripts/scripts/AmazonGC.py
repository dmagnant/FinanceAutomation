from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "AmazonGC":
    from Functions.GeneralFunctions import showMessage
    from Functions.WebDriverFunctions import openWebDriver
    from Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance
else:
    from .Functions.GeneralFunctions import showMessage
    from .Functions.WebDriverFunctions import openWebDriver
    from .Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance

def confirmAmazonGCBalance(driver):
    driver.execute_script("window.open('https://www.amazon.com/gc/balance');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    balance = driver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$')
    mybook = openGnuCashBook('Finance', True, True)
    amazonBalance = getGnuCashBalance(mybook, 'AmazonGC')
    if str(amazonBalance) != balance:
        showMessage("Amazon GC Mismatch", f'Amazon balance: {balance} \n' f'Gnu Cash balance: {amazonBalance} \n')
    return amazonBalance

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    balance = confirmAmazonGCBalance(driver)
    print(balance)

