from Eternl import runEternl
from Exodus import runExodus
from Functions.Functions import (openWebDriver, getGnuCashBalance, openGnuCashBook,
                       setDirectory, updateCryptoPrices)
from IoPay import runIoPay
from Kraken import runKraken
from Midas import runMidas
from MyConstant import runMyConstant
from Presearch import runPresearch


def runCrypto(directory, driver):
    updateCryptoPrices()
    driver.implicitly_wait(5)
    driver.get("https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=623829469")

    runMyConstant(directory, driver, "Crypto")
    runEternl(directory, driver)
    runKraken(directory, driver)
    runPresearch(directory, driver)
    runMidas(directory, driver)
    runExodus(directory)
    runIoPay(directory)

    Finance = openGnuCashBook(directory, 'Finance', True, True)
    cryptoBalance = round(getGnuCashBalance(Finance, 'Crypto'), 2)
    print(f'Crypto Portfolio worth: {cryptoBalance}')

    return cryptoBalance
if __name__ == '__main__':
    directory = setDirectory()
    driver = openWebDriver("Chrome")
    response = runCrypto(directory, driver)
