from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import subprocess, time, requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def getElementIfTextEquals(driver, text):
    try:
        elem = driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{text}")'
        )
        return elem
    except NoSuchElementException:
        return False

def launchAppiumServer(): 
    try: requests.get("http://127.0.0.1:4723/status", timeout=2)
    except Exception as e: subprocess.Popen(["cmd", "/k", "appium"], creationflags=subprocess.CREATE_NEW_CONSOLE)

def wakeUpDevice(): subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_WAKEUP"], check=True)

def launchApp(package):
    # Suppress monkey's stdout/stderr noise (bash arg, Events injected, etc.)
    subprocess.run(
        ["adb", "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

def createDriver(package, activity):
    caps = {"platformName": "Android","automationName": "UiAutomator2","deviceName": "AndroidDevice","udid": "3A250DLJH000R6",
            "appPackage": package,"appActivity": activity,"noReset": True,"fullReset": False,"newCommandTimeout": 6000}
    options = UiAutomator2Options().load_capabilities(caps)
    return webdriver.Remote(command_executor="http://127.0.0.1:4723",options=options)

def setupAndOpenInboxDollarsApp():
    launchAppiumServer()
    launchApp("com.mentormate.android.inboxdollars")
    driver = createDriver("com.mentormate.android.inboxdollars", "com.mentormate.android.inboxdollars.ui.activities.MainActivity")
    el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Offers")
    rect = el.rect
    x = rect["x"] + rect["width"] * 0.5
    y = rect["y"] + rect["height"] * 0.3  # a bit above center
    driver.execute_script("mobile: clickGesture",{"x": x, "y": y})
    time.sleep(1)
    tapjoy = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,f'new UiSelector().textContains("Tapjoy")')
    tapjoy.click()
    time.sleep(1)
    return driver

def setupAndOpenSwagbucksApp():
    launchAppiumServer()
    launchApp("com.prodege.swagiq")
    driver = createDriver("com.prodege.swagiq", "com.prodege.swagiq.android.home.HomeActivity")
    el = driver.find_element(AppiumBy.ID,"com.prodege.swagiq:id/btn_earn_more") # Tap to Earn More
    el.click()
    time.sleep(1)
    tapjoy = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,f'new UiSelector().textContains("Tapjoy")')
    tapjoy.click()
    time.sleep(1)
    return driver

def inboxDollarsApp(redemptionsNeeded=1):
    print("Starting InboxDollars script...")
    driver = setupAndOpenInboxDollarsApp()
    click_all_offers(driver, redemptionsNeeded=redemptionsNeeded)
    driver.quit()

def swagbucksApp(redemptionsNeeded=1):
    print("Starting Swagbucks script...")
    driver = setupAndOpenSwagbucksApp()
    click_all_offers(driver, redemptionsNeeded=redemptionsNeeded)
    driver.quit()

def scrollPage(driver, scrollUntilMoreOffers, existingOffers=None):
    SCROLLABLE = 'new UiScrollable(new UiSelector().scrollable(true))'
    existingOffersCount = len(existingOffers)
    newOffersCount = len(existingOffers)
    while existingOffersCount == newOffersCount:
        try:
            print("Scrolling to next page...")
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'{SCROLLABLE}.scrollForward()'
            )
        except Exception:
            print("exception when trying to scroll")
            return False
        offers = getListOfOffersAndAddToExisting(driver, existingOffers)
        newOffersCount = len(offers)
        print(f'found {len(offers)-len(existingOffers)} new offers after scrolling')
        if not scrollUntilMoreOffers:
            break
    return offers

def redeemOffer(driver, offerElement, offers, redeemedSinceLastScroll):
    while True:
        try:
            offerElement.click()
            print('clicked offer')
        except StaleElementReferenceException:
            print('stale element reference exception on clicking offer')
            if redeemedSinceLastScroll: offers = scrollPage(driver, True, existingOffers=offers)
            else:
                print('could not resolve stale offer element. failed offer')
                return False
            if offers:
                redeemedSinceLastScroll = False
                continue
            else:
                print('unable to scroll page')
                return False
        time.sleep(2)
        earn1sb = getElementIfTextEquals(driver, "Earn ")
        if earn1sb: earn1sb.click()
        else:
            print('unable to click ')
            if redeemedSinceLastScroll: offers = scrollPage(driver, False, offers)
            else:
                print('could not find earn 1 sb element. failed offer')
                return False
            if offers:
                redeemedSinceLastScroll = False
                continue
            else:
                print('unable to scroll page')
                return False
        time.sleep(6)
        driver.back()
        time.sleep(3)
        if getElementIfTextEquals(driver, "Earn "):
            driver.back()
            time.sleep(2)
        break
    redeemedSinceLastScroll = True
    return {'offers': offers, 'redeemedSinceLastScroll': redeemedSinceLastScroll}

def getListOfOffersAndAddToExisting(driver, existingOffers):
    try:
        offers = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().className("android.widget.TextView").text("1")')))
        print(f'Found {len(offers)} offers on the page.')
    except TimeoutException:
        offers = scrollPage(driver, True, existingOffers)
    if not existingOffers:
        existingOffers = offers
    elif len(offers) > len(existingOffers):
        new = offers[len(existingOffers):]
        existingOffers.extend(new)
        print(f'Added {len(new)} new offers.')
    return existingOffers

def click_all_offers(driver, existingOffers=None, redemptionsNeeded=5):
    offersRedeemed = 0
    offers = getListOfOffersAndAddToExisting(driver, existingOffers)
    offerAttempt = offersRedeemed
    redeemedSinceLastScroll = True
    while offersRedeemed < redemptionsNeeded:
        print(f"attempting: {offerAttempt+1}, redeemed: {offersRedeemed}, need: {redemptionsNeeded}")
        if offerAttempt > len(offers):
            offers = scrollPage(driver, True, offers)
        offer = offers[offerAttempt]
        redeemOfferResult = redeemOffer(driver, offer, offers, redeemedSinceLastScroll)
        offerAttempt += 1
        if not redeemOfferResult:
            print("Failed to redeem offer moving to the next.")
            continue
        else:
            offers = redeemOfferResult['offers']
            redeemedSinceLastScroll = redeemOfferResult['redeemedSinceLastScroll']
            print(f"Redeemed offer {offersRedeemed+1}")
            offersRedeemed += 1
    print(f"Total offers redeemed: {offersRedeemed}")

def runBothApps(swagBucksAmt=1, inboxDollarsAmt=1):
    if swagBucksAmt:
        swagbucksApp(swagBucksAmt)
        time.sleep(1)
    if inboxDollarsAmt:
        inboxDollarsApp(inboxDollarsAmt)

if __name__ == "__main__":
    # launchAppiumServer()
    # driver = createDriver("com.prodege.swagiq", "com.tapjoy.TJAdUnitActivity")
    driver = createDriver("com.mentormate.android.inboxdollars", "com.tapjoy.TJAdUnitActivity")
    # runBothApps()

    el = getElementIfTextEquals(driver, "Tapjoy")
    print(el)
    driver.quit()
