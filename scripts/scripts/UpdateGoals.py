import gspread
from datetime import datetime

if __name__ == '__main__' or __name__ == "UpdateGoals":
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.SpreadsheetFunctions import openSpreadsheet, getWorkSheet
else:
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.SpreadsheetFunctions import openSpreadsheet, getWorkSheet

def getTotalForIncomeExpenseAccounts(accountList, mybook, transactions, timeframe, date, accounts, accountsType, worksheet):
    for i in accountList:
        print(i)
        total, readBook = 0, mybook.readBook
        accountsToUpdate = [readBook.accounts(fullname=mybook.getGnuAccountFullName(i))]
        for acc in accountsToUpdate[0].children:    accountsToUpdate.append(acc)
        for acc in accountsToUpdate:
            for tr in transactions:
                for spl in tr.splits:
                    if spl.account.fullname == acc.fullname:
                        if "Income:" in acc.fullname or "'s Contributions" in acc.fullname:     value = -spl.value 
                        else:                                                                   value = spl.value
                        amount = format(value, ".2f")
                        total += float(amount)
        accounts[i.replace(' ','').replace('&','').replace('/','').replace("'",'')+'_'+accountsType] = round(total, 2)
        updateSpreadsheet(worksheet, i, date, total, accountsType, timeframe)
    return accounts

def getContributionsForRetirementAccounts(accountList, mybook, transactions, accountsContext, date, worksheet):
    accountsContext['HSAPersonalContributions'], accountsContext['IRAContributions'], accountsContext['RothIRAContributions'], accountsContext['401kPersonalContributions'], accountsContext['Roth401kContributions'], accountsContext['BrokerageContributions'], accountsContext['RothIRAContributions']=0,0,0,0,0
    for account in accountList:
        total = 0
        roth401kTotal = 0
        for tr in transactions:
            for spl in tr.splits:
                value = 0
                if spl.account.fullname == mybook.getGnuAccountFullName(account):
                    if "Paycheck" in tr.description:
                        if account == 'Optum Cash':
                            value = spl.value - 25
                        elif account == 'HE Cash' and tr.post_date.day < 20 and tr.post_date.month in [1,4,7,10]:
                            value = spl.value - 125
                        else:
                            value = spl.value
                    elif "Transfer" in tr.description:              value = spl.value
                    if value:                                       
                        if 'roth' in spl.memo: 
                            roth401kTotal += float(format(value, ".2f"))
                        else:
                            total += float(format(value, ".2f"))
        if account in ['Optum Cash', 'HE Cash']:                    accountsContext['HSAPersonalContributions'] += round(total, 2)
        elif account == 'IRA SPAXX':                                accountsContext['IRAContributions'] += round(total, 2)
        elif account == 'Roth IRA SPAXX':                           accountsContext['RothIRAContributions'] += round(total, 2)
        elif account in ['Brokerage SPAXX', 'GME']:                 accountsContext['BrokerageContributions'] += round(total, 2)
        elif account == 'Vanguard401k':                             
            accountsContext['401kPersonalContributions'] += round(total, 2)
            accountsContext['Roth401kContributions'] += round(roth401kTotal, 2)
    updateSpreadsheet(worksheet, '401k Contributions Personal', date, accountsContext['401kPersonalContributions'], 'Personal', 'YTD')
    updateSpreadsheet(worksheet, 'Roth 401k Contributions', date, accountsContext['Roth401kContributions'], 'Personal', 'YTD')
    updateSpreadsheet(worksheet, 'HSA Contributions Personal', date, accountsContext['HSAPersonalContributions'], 'Personal', 'YTD')
    updateSpreadsheet(worksheet, 'IRA Contributions', date, accountsContext['IRAContributions'], 'Personal', 'YTD')
    updateSpreadsheet(worksheet, 'Roth IRA Contributions', date, accountsContext['RothIRAContributions'], 'Personal', 'YTD')
    updateSpreadsheet(worksheet, 'Brokerage Contributions', date, accountsContext['BrokerageContributions'], 'Personal', 'YTD')
    
def getContributionsForCryptoCurrency(mybook, transactions, accountsContext, date, worksheet):
    readBook = mybook.readBook
    baseAccount = readBook.accounts(fullname='Assets:Non-Liquid Assets:CryptoCurrency')
    cryptoAccounts = [baseAccount]
    total = 0
    for acc in baseAccount.children:    cryptoAccounts.append(acc)
    for acc in cryptoAccounts:
        for tr in transactions:
            for spl in tr.splits:
                if spl.account.fullname == acc.fullname:
                    if tr.description == 'Crypto Purchase' or 'DIGITALOCEAN' in tr.description:
                        total += float(format(spl.value, ".2f"))
    accountsContext['CryptoContributions'] = round(total, 2)
    updateSpreadsheet(worksheet, 'Crypto Contributions', date, accountsContext['CryptoContributions'], 'Personal', 'YTD')

def getAssetAccountBalances(date, accountList, book, accountsType, timeframe, worksheet):
    for account in accountList:
        value = float(book.getGnuAccountBalance(book.getGnuAccountFullName(account), date))
        if account == 'IRA':
            value += float(book.getGnuAccountBalance(book.getGnuAccountFullName('Roth IRA'), date))
        elif account == 'Brokerage':
            value += float(book.getGnuAccountBalance(book.getGnuAccountFullName('GME'), date) * book.getPriceInGnucash('GME'))
        updateSpreadsheet(worksheet, account, date, round(value,2), accountsType, timeframe)

def getCellForMonthly(account, month, accounts='Personal'):
    rowStart = 76 if accounts == 'Personal' else 25
    row = str(rowStart + (month - 1))
    match account:
        case 'Amazon':                  return 'C' + row if accounts == 'Personal' else 'B' + row
        case 'Bars & Restaurants':      return 'D' + row if accounts == 'Personal' else 'C' + row
        case 'Entertainment':           return 'E' + row if accounts == 'Personal' else 'D' + row
        case 'Other':                   return 'G' + row if accounts == 'Personal' else 'J' + row    
        # Personal
        case 'Joint Expenses':          return 'F' + row
        case 'Dividends':               return 'L' + row
        case 'Interest':                return 'M' + row
        case 'Market Research':         return 'N' + row
        # Joint
        case 'Groceries':               return 'E' + row
        case 'Home Depot':              return 'F' + row
        case 'Home Expenses':           return 'G' + row
        case 'Home Furnishings':        return 'H' + row
        case 'Mortgage Principle':      return 'I' + row
        case 'Pet':                     return 'K' + row
        case 'Travel':                  return 'L' + row
        case 'Utilities':               return 'M' + row
        case "Dan's Contributions":     return 'Q' + row
        case "Tessa's Contributions":   return 'R' + row  
        case _:                         print('Month cell not found for: ' + account)
        
def getCellForYTD(account, accountsType):
    column = 'G' if accountsType == 'Personal' else 'F'   
    match account:
        # Joint and Personal
        case 'Amazon':                          return column + str(22) if accountsType == 'Personal' else column + str(7)
        case 'Bars & Restaurants':              return column + str(24) if accountsType == 'Personal' else column + str(8)
        case 'Entertainment':                   return column + str(26) if accountsType == 'Personal' else column + str(9)
        case 'Groceries':                       return column + str(27) if accountsType == 'Personal' else column + str(10)
        case 'Other':                           return column + str(31) if accountsType == 'Personal' else column + str(15)
        # Personal
        case '401k Contributions':              return column + str(2)
        case 'Dividends':                       return column + str(3)
        case 'HSA Contributions':               return column + str(4)
        case 'Interest':                        return column + str(5)
        case 'Pension Contributions':           return column + str(6)
        case 'Market Research':                 return column + str(7)
        case 'Salary':                          return column + str(8)
        case '401k Contributions Personal':     return column + str(12)
        case 'Brokerage Contributions':         return column + str(13) 
        case 'Crypto Contributions':            return column + str(14)
        case 'HSA Contributions Personal':      return column + str(15)
        case 'IRA Contributions':               return column + str(16)
        case 'Roth 401k Contributions':         return column + str(17)
        case 'Roth IRA Contributions':          return column + str(18)
        case 'Bank Fees':                       return column + str(23)
        case 'Clothing/Apparel':                return column + str(25)
        case 'Income Taxes':                    return column + str(28)
        case 'Joint Expenses':                  return column + str(29)
        case 'Medical':                         return column + str(30)
        case 'Loan Interest':                   return column + str(32) 
        case 'Loan Principle':                  return column + str(33)         
        case 'Transportation':                  return column + str(34)
        case 'Vanguard401k':                    return column + str(62)
        case 'Brokerage':                       return column + str(63)
        case 'Crypto':                          return column + str(64)
        case 'HSA':                             return column + str(65)
        case 'IRA':                             return column + str(66)
        case 'Liquid Assets':                   return column + str(67)
        case 'Pension':                         return column + str(68)
        case 'Roth IRA':                        return column + str(69)
        # Joint
        case "Dan's Contributions":             return column + str(2)                 
        case "Tessa's Contributions":           return column + str(3)         
        case 'Home Depot':                      return column + str(11)
        case 'Home Expenses':                   return column + str(12)
        case 'Home Furnishings':                return column + str(13)
        case 'Mortgage Principle':              return column + str(14)
        case 'Pet':                             return column + str(16)
        case 'Travel':                          return column + str(17)
        case 'Utilities':                       return column + str(18)
        
        case _:                                 print('YTD cell not found for: ' + account)

# def getWorkSheet(accountsType):
#     jsonCreds = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
#     sheetTitle = 'Finances' if accountsType == 'Personal' else 'Home'
#     sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
#     worksheetTitle = 'Goals' if accountsType == 'Personal' else 'Finances'
#     return sheet.worksheet(worksheetTitle)

def updateSpreadsheet(worksheet, account, date, value, accountsType, timeframe):
    cell = getCellForMonthly(account, date.month, accountsType) if timeframe == 'Month' else getCellForYTD(account, accountsType)
    worksheet.update_acell(cell, value)

def runUpdateGoals(accountsType, timeframe, book):
    driver = Driver("Chrome")
    if accountsType == 'Personal':
        sheetTitle = 'Finances'
        tabTitle = 'Goals'
    else:
        sheetTitle = 'Home'
        tabTitle = 'Finances'
    openSpreadsheet(driver, sheetTitle, tabTitle)
    worksheet = getWorkSheet(sheetTitle, tabTitle)
    dateRange = getStartAndEndOfDateRange(datetime.today().date(), timeframe)
    transactions = book.getTransactionsByDateRange(dateRange)
    incomeAndExpenseAccounts, incomeQuarterlyAccounts, expenseQuarterlyAccounts, retirementContributionAccounts = [], [], [], []
    accountsContext = {}
    commonExpenseAccounts = ['Amazon', 'Bars & Restaurants', 'Entertainment', 'Other', 'Groceries']
    if accountsType == 'Personal':
        specificIncomeAccounts = ['Dividends','Interest','Market Research']
        specificExpenseAccounts = ['Joint Expenses']
        if timeframe == 'YTD':
            incomeQuarterlyAccounts = ['401k Contributions', 'HSA Contributions', 'Pension Contributions', 'Salary']
            expenseQuarterlyAccounts = ['Bank Fees', 'Clothing/Apparel', 'Income Taxes', 'Medical', 'Loan Interest', 'Loan Principle', 'Transportation']
            retirementContributionAccounts = ['Vanguard401k', 'Optum Cash', 'HE Cash', 'IRA SPAXX', 'Roth IRA SPAXX', 'Brokerage SPAXX', 'GME']
            assetAccounts = ['Vanguard401k', 'Crypto', 'Liquid Assets', 'Pension', 'HSA', 'IRA', 'Brokerage', 'Roth IRA']
        else:   commonExpenseAccounts.remove('Groceries')
    elif accountsType == 'Joint':
        specificIncomeAccounts = ["Dan's Contributions", "Tessa's Contributions"]
        specificExpenseAccounts = ['Home Depot','Home Expenses','Home Furnishings','Pet','Travel','Utilities', 'Mortgage Principle']
    
    incomeAndExpenseAccounts.extend(specificIncomeAccounts);  incomeAndExpenseAccounts.extend(incomeQuarterlyAccounts)
    incomeAndExpenseAccounts.extend(commonExpenseAccounts);  incomeAndExpenseAccounts.extend(specificExpenseAccounts);    incomeAndExpenseAccounts.extend(expenseQuarterlyAccounts)
    
    getTotalForIncomeExpenseAccounts(incomeAndExpenseAccounts, book, transactions, timeframe, dateRange['endDate'], accountsContext, accountsType, worksheet)
    if retirementContributionAccounts:
        getContributionsForRetirementAccounts(retirementContributionAccounts, book, transactions, accountsContext, dateRange['endDate'], worksheet)
        getContributionsForCryptoCurrency(book, transactions, accountsContext, dateRange['endDate'], worksheet)
        getAssetAccountBalances(dateRange['endDate'], assetAccounts, book, accountsType, timeframe, worksheet)
    return accountsContext
    
if __name__ == '__main__':
    # accounts = 'Joint' # Personal or Joint
    # timeframe = "Month" # Month or YTD
    # book = GnuCash('Finance') if accounts == 'Personal' else GnuCash('Home')
    # runUpdateGoals(accounts, timeframe, book)
    # book.closeBook()
    
    date = datetime.today().date()
    book = GnuCash('Finance')
    print(float(book.getGnuAccountBalance(book.getGnuAccountFullName('GME'), date) * book.getPriceInGnucash('GME')))


