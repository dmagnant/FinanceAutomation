from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "AmazonGC":
    from Functions import (openGnuCashBook, openWebDriver, setDirectory,
                           showMessage)
else:
    from .Functions import openGnuCashBook, setDirectory, showMessage

def confirmAmazonGCBalance(driver):
    directory = setDirectory()
    driver.execute_script("window.open('https://www.amazon.com/gc/balance');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    balance = driver.find_element(By.ID, "gc-ui-balance-gc-balance-value").text.strip('$')
    mybook = openGnuCashBook(directory, 'Finance', True, True)
    with mybook as book:
        amazonBalance = mybook.accounts(fullname="Assets:Liquid Assets:Amazon GC").get_balance()
        book.close()
    if str(amazonBalance) != balance:
        showMessage("Amazon GC Mismatch", f'Amazon balance: {balance} \n' f'Gnu Cash balance: {amazonBalance} \n')

if __name__ == '__main__':
    driver = openWebDriver("Chrome")
    confirmAmazonGCBalance(driver)
