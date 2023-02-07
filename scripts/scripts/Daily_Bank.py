from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import threading

if __name__ == '__main__' or __name__ == "Daily_Bank":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import showMessage
    from Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook
    from Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet
    from Paypal import runPaypal
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout    
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD
    from .Classes.WebDriver import Driver
    from .Functions.GeneralFunctions import showMessage
    from .Functions.GnuCashFunctions import purgeOldGnucashFiles, openGnuCashUI, openGnuCashBook
    from .Functions.SpreadsheetFunctions import updateCryptoPrices, openSpreadsheet
    from .Paypal import runPaypal
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout

def runDailyBank():
    driver = Driver("Chrome")
    Crypto = USD("Crypto")
    sofi = runSofi(driver)
    ally = runAlly(driver)
    presearchRewardsRedemptionAndBalanceUpdates(driver)
    runPaypal(driver)
    openSpreadsheet(driver, 'Checking Balance', '2023')
    openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    updateCryptoPrices(driver)
    Crypto.updateGnuBalance(openGnuCashBook('Finance', True, True))
    openSpreadsheet(driver, 'Home', '2023 Balance')
    if sofi[0].reviewTransactions or sofi[1].reviewTransactions:
        openGnuCashUI('Finances')
    if ally.reviewTransactions:
        openGnuCashUI('Home')
    driver.openNewWindow('https://finance.yahoo.com/quote/GME/')
    try:
        driver.webDriver.find_element(By.XPATH,"//*[@id='myLightboxContainer']/section/button[1]/svg").click()
    except NoSuchElementException:
        exception = 'pop-up window not there'
    GMEprice = driver.webDriver.find_element(By.XPATH,"/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/div/div[3]/div[1]/div/fin-streamer[1]").text
    showMessage("Balances + Review", 
        f'Sofi Checking: {sofi[0].balance} \n'
        f'  Gnu Balance: {sofi[0].gnuBalance} \n \n'
        f' Sofi Savings: {sofi[1].balance} \n'
        f' Gnu Balance: {sofi[1].gnuBalance} \n \n'
        f'Ally Checking: {ally.balance} \n'
        f'  Gnu Balance: {ally.gnuBalance} \n \n'
        f'Crypto Balance: {round(Crypto.gnuBalance, 2)} \n \n'
        f'GME Price: {GMEprice} \n \n'
        f'Review transactions (Sofi Checking):\n {sofi[0].reviewTransactions} \n'
        f'Review transactions (Sofi Savings):\n {sofi[1].reviewTransactions} \n'
        f'Review transactions (Ally):\n {ally.reviewTransactions}')
    sofiLogout(driver)
    allyLogout(driver)
    driver.closeWindowsExcept([':8000/', 'swagbucks.com'])
    purgeOldGnucashFiles()

if __name__ == '__main__':
    runDailyBank()
    # driver = Driver("Chrome")
    # # updateCryptoPrices(driver)
    
    # x = threading.Thread(target=locateSofiWindow, args=(driver,))
    # y = threading.Thread(target=locateAllyWindow, args=(driver,))
    # z = threading.Thread(target=locatePayPalWindow, args=(driver,))
    # x.start()
    # y.start()
    # z.start()