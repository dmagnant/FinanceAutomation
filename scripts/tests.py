from django.test import TestCase
from scripts.Sofi import *
from scripts.Ally import *
from scripts.AmazonGC import *
from scripts.Amex import *
from scripts.Barclays import *
from scripts.Bing import *
from scripts.BoA import *
from scripts.Chase import *
from scripts.Coinbase import *
from scripts.Cointiply import *
from scripts.Daily_Bank import *
from scripts.Daily_MR import *
from scripts.Discover import *
from scripts.Eternl import *
from scripts.Exodus import *
from scripts.Fidelity import *
from scripts.HealthEquity import *
from scripts.IoPay import *
from scripts.Kraken import *
from scripts.Ledger import *
from scripts.Monthly_Bank import *
from scripts.MyConstant import *
from scripts.Paypal import *
from scripts.Paidviewpoint import *
from scripts.Pinecone import *
from scripts.Presearch import *
from scripts.PSCoupons import *
from scripts.Sofi import *
from scripts.Swagbucks import *
from scripts.Tellwut import *
from scripts.UpdateGoals import *
from scripts.Vanguard import *
from scripts.Worthy import *
from scripts.Classes.WebDriver import Driver

def driverSetup():
    return Driver("Chrome")

# Create your tests here.
class SofiTest(TestCase):
    def __init__(self, driver):
        self.driver = driver
        self.runTests()
        
    def loginTest(self):
        result = locateSofiWindow(self.driver)
        self.assertTrue(result)
    
    def balanceTest(self):
        Checking = USD("Sofi Checking")
        getSofiBalanceAndOrientPage(self.driver, Checking)
        balance = round(float(Checking.balance), 0)
        self.assertGreater(int(balance), 0, 'balance not greater than 0')

    def runTests(self):
        self.loginTest()
        self.balanceTest()
        sofiLogout(self.driver)

class AllyTest(TestCase):
    def __init__(self, driver):
        self.driver = driver
        self.runTests()
            
    def loginTest(self):
        result = locateAllyWindow(self.driver)
        self.assertTrue(result)
    
    def balanceTest(self):
        balance = round(float(getAllyBalance(driver)), 0)
        self.assertGreater(int(balance), 0, 'balance not greater than 0')

    def runTests(self):
        self.loginTest()
        self.balanceTest()
        allyLogout(self.driver)

if __name__ == '__main__':
    driver = driverSetup()
    SofiTest(driver)
    AllyTest(driver)
    
    driver.closeWindowsExcept([':8000/'])
