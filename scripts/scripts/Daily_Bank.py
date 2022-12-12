import os
import os.path

if __name__ == '__main__' or __name__ == "Daily_Bank":
    from Ally import allyLogout, runAlly
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import setDirectory, showMessage
    from Functions.GnuCashFunctions import purgeOldGnucashFiles
    from Functions.SpreadsheetFunctions import updateCryptoPrices
    from Paypal import runPaypal
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout    
else:
    from .Ally import allyLogout, runAlly
    from .Classes.Asset import USD
    from .Classes.WebDriver import Driver
    from .Functions.GeneralFunctions import setDirectory, showMessage
    from .Functions.GnuCashFunctions import purgeOldGnucashFiles
    from .Functions.SpreadsheetFunctions import updateCryptoPrices
    from .Paypal import runPaypal
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout

def runDailyBank():
    directory = setDirectory()
    driver = Driver("Chrome")
    Crypto = USD("Crypto")
    sofi = runSofi(driver)
    ally = runAlly(driver)
    presearchRewardsRedemptionAndBalanceUpdates(driver)
    runPaypal(driver)
    driver.webDriver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=382679207');")
    driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
    driver.webDriver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=623829469');")
    driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
    updateCryptoPrices(driver)
    driver.webDriver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/edit#gid=317262693');")
    driver.webDriver.switch_to.window(driver.webDriver.window_handles[len(driver.webDriver.window_handles)-1])
    if sofi[0].reviewTransactions or sofi[1].reviewTransactions:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    if ally.reviewTransactions:
        os.startfile(directory + r"\Stuff\Home\Finances\Home.gnucash")
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
    runDailyBank()
    # driver = Driver("Chrome")    
    # updateCryptoPrices(driver.webDriver)