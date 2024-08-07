import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
if __name__ == '__main__' or __name__ == "PSCoupons":
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getPassword, showMessage)
else:
    from .Functions.GeneralFunctions import (getPassword, showMessage)

def locatePSCouponWindow(driver):
    found = driver.findWindowByUrl("picknsave.com/savings/cl/coupons/")
    if not found:   psCouponLogin(driver)
    else:           driver.webDriver.switch_to.window(found); time.sleep(1)

def psCouponLogin(driver):
    driver.openNewWindow('https://www.picknsave.com/savings/cl/coupons/')
    try:    driver.webDriver.find_element(By.ID, 'SignIn-submitButton').click()
    except NoSuchElementException:  exception = 'already logged in'
    
def setPSCouponFilters(driver):
    driver.webDriver.find_element(By.ID,"Filter-item-In-Store").click() # In-Store
    time.sleep(1)
    departmentList = ["Adult-Beverage", 'Bakery', "Baking-Goods", 'Beauty', "Breakfast", "Canned-& Packaged", "Dairy", "Frozen", "Natural-& Organic", "Pasta-Sauces Grain", "Personal-Care", "Produce", "Snacks"]
    for dept in departmentList: driver.webDriver.find_element(By.ID,"Filter-item-" + dept).click(); time.sleep(1)
    driver.webDriver.find_element(By.ID,"new-coupons-filer").click() # last 7 days
    driver.webDriver.execute_script("window.scrollTo(0, 0)")

def clipCoupons(driver):
    def getCouponBaseElement(num): return "//*[@id='content']/section/div/section[2]/section/section/div/div[2]/div[2]/div/div/div/ul/li[" + str(num) + "]/div/div/div/div[2]/div["
    
    couponTextPathEnd, couponClipButtonPathEnd, num, scrollY = "1]/div/div[1]/h3", "3]/button[2]", 1 ,1900
    while True:
        try:
            couponText = driver.webDriver.find_element(By.XPATH,getCouponBaseElement(num)+couponTextPathEnd).text
            print(couponText)
            clipCouponButton = driver.webDriver.find_element(By.XPATH,getCouponBaseElement(num)+couponClipButtonPathEnd)
            if clipCouponButton.text.lower() == "clip": clipCouponButton.click()
            num += 1
            time.sleep(1)
            if num % 24 == 0:
                print("Scroll now")
                driver.webDriver.execute_script("window.scrollTo(0, " + str(scrollY) + ")")
                scrollY -= 2100
                driver.webDriver.execute_script("window.scrollTo(0, " + str(scrollY) + ")")
                scrollY += 4200
        except NoSuchElementException:  break

def runPSCoupon(driver):
    locatePSCouponWindow(driver)
    setPSCouponFilters(driver)
    # clipCoupons(driver)

if __name__ == '__main__':
    driver = Driver("Chrome")
    setPSCouponFilters(driver)
    
    # locatePSCouponWindow(driver)
    # scrollY = 3800
    # driver.webDriver.execute_script("window.scrollTo(0, " + str(scrollY) + ")")
