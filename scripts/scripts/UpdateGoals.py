from datetime import datetime
import gspread

if __name__ == '__main__' or __name__ == "UpdateGoals":
    from Classes.WebDriver import Driver
    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                            setDirectory, showMessage)
    from Functions.GnuCashFunctions import openGnuCashBook
    from Functions.SpreadsheetFunctions import openSpreadsheet
else:
    from .Classes.WebDriver import Driver
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,
                                             setDirectory, showMessage)
    from .Functions.GnuCashFunctions import openGnuCashBook
    from .Functions.SpreadsheetFunctions import openSpreadsheet


def getTransactionTotal(dateRange, gnuAccount, mybook):
    total = 0
    # retrieve transactions from GnuCash
    transactions = [tr for tr in mybook.transactions
                    if tr.post_date >= dateRange[0] and tr.post_date <= dateRange[1]
                    for spl in tr.splits
                    if spl.account.fullname == gnuAccount]
    for tr in transactions:
        date = str(tr.post_date.strftime('%Y-%m-%d'))
        description = str(tr.description)
        for spl in tr.splits:
            if spl.account.fullname == gnuAccount:
                if "Income:" in gnuAccount or "'s Contributions" in gnuAccount:
                    value = -spl.value 
                else:
                    value = spl.value
                amount = format(value, ".2f")
                total += float(amount)
    return total

def getTotalForEachAccount(accountList, mybook, dateRange, timeframe, directory, month, accounts="Personal"):
    for i in accountList:
        totalTransactions = compileGnuTransactions(i, mybook, dateRange)
        if timeframe == "Month":
            updateSpreadsheet(directory, i, month, totalTransactions, accounts)
        else:
            print(i)
            print(totalTransactions)

def compileGnuTransactions(account, mybook, dateRange):
    def matchAccount():
        match account:
            case 'Amazon':
                return 'Expenses:Amazon'
            case 'Bank Fees':
                return 'Expenses:Bank Fees'            
            case 'Bars & Restaurants':
                return 'Expenses:Bars & Restaurants'
            case 'CC Rewards':
                return 'Income:Credit Card Rewards'
            case 'Clothing/Apparel':
                return 'Expenses:Clothing/Apparel'            
            case 'Dan':
                return "Dan's Contributions"
            case 'Dividends':
                return 'Income:Investments:Dividends'
            case 'Entertainment':
                return 'Expenses:Entertainment'
            case 'Groceries':
                return 'Expenses:Groceries'
            case 'Home Depot':
                return 'Expenses:Home Depot'
            case 'Home Expenses':
                return 'Expenses:Home Expenses'
            case 'Home Furnishings':
                return 'Expenses:Home Furnishings'
            case 'HSA Contributions':
                return 'Income:Employer HSA Contributions'
            case 'Income Taxes':
                return 'Expenses:Income Taxes'                      
            case 'Interest':
                return 'Income:Investments:Interest'
            case 'Joint Expenses':
                return 'Expenses:Joint Expenses'
            case 'Loan Interest':
                return 'Expenses:Loan Interest'
            case 'Loan Principle':
                return 'Liabilities:Loans:Personal Loan'                             
            case 'Market Change':
                return 'Income:Investments:Market Change'            
            case 'Market Research':
                return 'Income:Market Research'
            case 'Medical':
                return 'Expenses:Medical'            
            case 'Other':
                return 'Expenses:Other'
            case 'Pension Contributions':
                return 'Income:Employer Pension Contributions'               
            case 'Pet':
                return 'Expenses:Pet'
            case 'Salary':
                return 'Income:Salary'              
            case 'Tessa':
                return "Tessa's Contributions"
            case 'Transportation':
                return 'Expenses:Transportation'              
            case 'Travel':
                return 'Expenses:Travel'
            case 'Ultimate':
                return 'Expenses:Ultimate'              
            case 'Utilities':
                return 'Expenses:Utilities'
    gnuAccount = matchAccount()
    
    total = 0
    accountChildren = mybook.accounts(fullname=gnuAccount).children
    total += getTransactionTotal(dateRange, gnuAccount, mybook)
    if len(accountChildren) > 0:
        for account in accountChildren:
            total += getTransactionTotal(dateRange, account.fullname, mybook)
    return total

def getCell(account, month, accounts='Personal'):
    rowStart = 48 if accounts == 'Personal' else 25
    row = str(rowStart + (month - 1))
    match account:
        case 'Amazon':
            return 'C' + row if accounts == 'Personal' else 'B' + row
        case 'Bars & Restaurants':
            return 'D' + row if accounts == 'Personal' else 'C' + row
        case 'CC Rewards':
            return 'L' + row
        case 'Dan':
            return 'Q' + row
        case 'Dividends':
            return 'M' + row
        case 'Entertainment':
            return 'E' + row if accounts == 'Personal' else 'D' + row
        case 'Groceries':
            return 'E' + row
        case 'Home Depot':
            return 'F' + row
        case 'Home Expenses':
            return 'G' + row
        case 'Home Furnishings':
            return 'H' + row
        case 'Interest':
            return 'N' + row
        case 'Joint Expenses':
            return 'F' + row
        case 'Market Research':
            return 'O' + row
        case 'Other':
            return 'G' + row if accounts == 'Personal' else 'J' + row
        case 'Pet':
            return 'K' + row
        case 'Tessa':
            return 'R' + row         
        case 'Travel':
            return 'L' + row
        case 'Utilities':
            return 'M' + row

def updateSpreadsheet(directory, account, month, value, accounts='Personal'):
    jsonCreds = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheetTitle = 'Asset Allocation' if accounts == 'Personal' else 'Home'
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheetTitle = 'Goals' if accounts == 'Personal' else 'Finances'
    worksheet = sheet.worksheet(worksheetTitle)
    cell = getCell(account, month, accounts)
    worksheet.update(cell, value)

def runUpdateGoals(accounts, timeframe):
    directory = setDirectory()
    driver = Driver("Chrome")
    if accounts == "Personal":
        openSpreadsheet(driver.webDriver, 'Asset Allocation', 'Goals')
    elif accounts == "Joint":
        openSpreadsheet(driver.webDriver, 'Home', '2022 Balance')
    today = datetime.today()
    dateRange = getStartAndEndOfDateRange(today, today.month, today.year, timeframe)
    mybook = openGnuCashBook('Finance', True, True) if accounts == 'Personal' else openGnuCashBook('Home', False, False)
    
    incomeAccounts = []
    expenseAccounts = []
    specificIncomeAccounts = []
    specificExpenseAccounts = []
    incomeQuarterlyAccounts = []
    expenseQuarterlyAccounts = []
    commonExpenseAccounts = ['Amazon', 'Bars & Restaurants', 'Entertainment', 'Other', 'Groceries']
    if accounts == 'Personal':
        specificIncomeAccounts = ['CC Rewards','Dividends','Interest','Market Research']
        specificExpenseAccounts = ['Joint Expenses']
        if timeframe == 'YTD':
            incomeQuarterlyAccounts = ['HSA Contributions', 'Pension Contributions', 'Market Change', 'Salary']
            expenseQuarterlyAccounts = ['Bank Fees', 'Clothing/Apparel', 'Income Taxes', 'Medical', 'Loan Interest', 'Loan Principle', 'Transportation', 'Ultimate']
        else:
            commonExpenseAccounts.remove('Groceries')
    elif accounts == 'Joint':
        specificIncomeAccounts = ['Dan','Tessa']
        specificExpenseAccounts = ['Home Depot','Home Expenses','Home Furnishings','Pet','Travel','Utilities']
    
    incomeAccounts.extend(specificIncomeAccounts)
    incomeAccounts.extend(incomeQuarterlyAccounts)
    incomeAccounts.sort()
    
    expenseAccounts.extend(commonExpenseAccounts)
    expenseAccounts.extend(specificExpenseAccounts)
    expenseAccounts.extend(expenseQuarterlyAccounts)
    expenseAccounts.sort()
    
    getTotalForEachAccount(incomeAccounts, mybook, dateRange, timeframe, directory, dateRange[1].month, accounts)
    getTotalForEachAccount(expenseAccounts, mybook, dateRange, timeframe, directory, dateRange[1].month, accounts)

if __name__ == '__main__':
    accounts = 'Personal' # Personal or Joint
    timeframe = "Month" # Month or YTD
    runUpdateGoals(accounts, timeframe)
