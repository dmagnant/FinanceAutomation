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
    openSpreadsheet(driver.webDriver, 'Checking Balance', '2022')
    openSpreadsheet(driver.webDriver, 'Asset Allocation', 'Cryptocurrency')
    updateCryptoPrices(driver)
    Crypto.updateGnuBalance(openGnuCashBook('Finance', True, True))
    openSpreadsheet(driver.webDriver, 'Home', '2022 Balance')
    if sofi[0].reviewTransactions or sofi[1].reviewTransactions:
        openGnuCashUI('Finances')
    if ally.reviewTransactions:
        openGnuCashUI('Home')
    showMessage("Balances + Review", 
        f'Sofi Checking: {sofi[0].balance} \n'
        f'  Gnu Balance: {sofi[0].gnuBalance} \n \n'
        f' Sofi Savings: {sofi[1].balance} \n'
        f' Gnu Balance: {sofi[1].gnuBalance} \n \n'
        f'Ally Checking: {ally.balance} \n'
        f'  Gnu Balance: {ally.gnuBalance} \n \n'
        f'Crypto Balance: {round(Crypto.gnuBalance, 2)} \n \n'
        f'Review transactions (Sofi Checking):\n {sofi[0].reviewTransactions} \n'
        f'Review transactions (Sofi Savings):\n {sofi[1].reviewTransactions} \n'
        f'Review transactions (Ally):\n {ally.reviewTransactions}')
    sofiLogout(driver)
    allyLogout(driver)
    while len(driver.webDriver.window_handles) > 1:
        driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
        driver.webDriver.close()
    purgeOldGnucashFiles()

if __name__ == '__main__':
    # runDailyBank()
    driver = Driver("Chrome")
    updateCryptoPrices(driver)
    