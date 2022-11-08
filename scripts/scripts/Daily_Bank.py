import os
import os.path

if __name__ == '__main__' or __name__ == "Daily_Bank":
    from Functions.GeneralFunctions import showMessage, setDirectory
    from Functions.WebDriverFunctions import openWebDriver
    from Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance
    from Functions.SpreadsheetFunctions import updateCryptoPrices
    from Ally import runAlly, allyLogout
    from Paypal import runPaypal
    from Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from Sofi import runSofi, sofiLogout
else:
    from .Functions.GeneralFunctions import showMessage, setDirectory
    from .Functions.WebDriverFunctions import openWebDriver
    from .Functions.GnuCashFunctions import openGnuCashBook, getGnuCashBalance
    from .Functions.SpreadsheetFunctions import updateCryptoPrices
    from .Ally import runAlly, allyLogout
    from .Paypal import runPaypal
    from .Presearch import presearchRewardsRedemptionAndBalanceUpdates
    from .Sofi import runSofi, sofiLogout

def runDailyBank():
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    driver.implicitly_wait(5)
    sofi = runSofi(driver)
    presearchRewardsRedemptionAndBalanceUpdates(driver)
    Finance = openGnuCashBook('Finance', True, True)
    sofiCheckingGnu = getGnuCashBalance(Finance, 'Sofi Checking')
    sofiSavingsGnu = getGnuCashBalance(Finance, 'Sofi Savings')
    runPaypal(driver)
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/edit#gid=382679207');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=623829469');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    updateCryptoPrices()
    cryptoBalance = round(getGnuCashBalance(Finance, 'Crypto'), 2)
    ally = runAlly(driver)
    Home = openGnuCashBook('Home', True, True)
    allyGnu = getGnuCashBalance(Home, 'Ally')
    driver.execute_script("window.open('https://docs.google.com/spreadsheets/d/1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/edit#gid=317262693');")
    if sofi[0][1] or sofi[1][1]:
        os.startfile(directory + r"\Finances\Personal Finances\Finance.gnucash")
    if ally[1]:
        os.startfile(directory + r"\Stuff\Home\Finances\Home.gnucash")
    showMessage("Balances + Review", 
        f'Sofi Checking: {sofi[0][0]} \n'
        f'  Gnu Balance: {sofiCheckingGnu} \n \n'
        f' Sofi Savings: {sofi[1][0]} \n'
        f'  Gnu Balance: {sofiSavingsGnu} \n \n'
        f'Ally Checking: {ally[0]} \n'
        f'  Gnu Balance: {allyGnu} \n \n'
        f'Crypto Balance: {cryptoBalance} \n \n'
        f'Review transactions (Sofi Checking):\n {sofi[0][1]} \n'
        f'Review transactions (Sofi Savings):\n {sofi[1][1]} \n'
        f'Review transactions (Ally):\n {ally[1]}')
    sofiLogout(driver)
    allyLogout(driver)
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
        driver.close()

if __name__ == '__main__':
    runDailyBank()
