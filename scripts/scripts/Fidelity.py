import time

from selenium.webdriver.common.by import By

if __name__ == '__main__' or __name__ == "Fidelity":
    from Classes.Asset import USD
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (showMessage, getPassword)    
else:
    from .Classes.Asset import USD
    from .Functions.GeneralFunctions import (showMessage, getPassword)    
    
def locateFidelityWindow(driver):
    found = driver.findWindowByUrl("digital.fidelity.com")
    if not found:
        fidelityLogin(driver)
    else:
        driver.webDriver.switch_to.window(found)
        time.sleep(1)

def fidelityLogin(driver):
    driver.openNewWindow('https://digital.fidelity.com/prgw/digital/login/full-page')
    driver.webDriver.refresh()
    # time.sleep(1)
    # driver.webDriver.find_element(By.ID,'password').send_keys(getPassword('Fidelity')) # pre-filled
    time.sleep(2)
    driver.webDriver.find_element(By.ID,'fs-login-button').click() # login

def getFidelityBalance(driver):
    locateFidelityWindow(driver)
    return driver.webDriver.find_element(By.XPATH,"/html/body/ap143528-portsum-dashboard-root/dashboard-root/div/div[3]/accounts-selector/nav/div[2]/div[2]/div/pvd3-link/s-root/span/a/span/s-slot/s-assigned-wrapper/div/div/div[2]/div/span[2]").text.replace('$','').replace(',','')

def runFidelity(driver, account):
    locateFidelityWindow(driver)
    account.setBalance(getFidelityBalance(driver))

if __name__ == '__main__':
    driver = Driver("Chrome")
    Fidelity = USD("Fidelity")
    runFidelity(driver, Fidelity)
    Fidelity.getData()
