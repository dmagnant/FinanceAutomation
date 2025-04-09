import gspread
from datetime import datetime

if __name__ == '__main__' or __name__ == "UpdateGoals":
    from Classes.WebDriver import Driver
    from Classes.GnuCash import GnuCash
    from Classes.Spreadsheet import Spreadsheet

    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,setDirectory, showMessage)
else:
    from .Classes.WebDriver import Driver
    from .Classes.GnuCash import GnuCash
    from .Classes.Spreadsheet import Spreadsheet
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,setDirectory, showMessage)

def getTotalForIncomeExpenseAccounts(accountList, mybook, transactions, timeframe, date, accounts, accountsType, spreadsheet):
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
        if (timeframe=='YTD'):                
            accounts[i.replace(' ','').replace('&','').replace('/','').replace("'",'')+'_'+accountsType] = round(total, 2)
        updateSpreadsheet(spreadsheet, i, date, total, accountsType, timeframe)
    return accounts

def getContributionsForRetirementAccounts(accountList, mybook, transactions, accountsContext, date, spreadsheet):
    accountsContext['HSAPersonalContributions'], accountsContext['IRAContributions'], accountsContext['RothIRAContributions'], accountsContext['401kPersonalContributions'], accountsContext['Roth401kContributions'], accountsContext['BrokerageContributions'], accountsContext['RothIRAContributions']=0,0,0,0,0,0,0
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
        if account in ['Optum Cash', 'HE Cash']:                                    accountsContext['HSAPersonalContributions'] += round(total, 2)
        elif account == 'FidelityIRASPAXX':                                         accountsContext['IRAContributions'] += round(total, 2)
        elif account == 'FidelityRothIRASPAXX':                                     accountsContext['RothIRAContributions'] += round(total, 2)
        elif account in ['FidelityBrokerageSPAXX', 'GME', 'WebullBrokerageCash']:   accountsContext['BrokerageContributions'] += round(total, 2)
        elif account == 'Vanguard401k':                             
            accountsContext['401kPersonalContributions'] += round(total, 2)
            accountsContext['Roth401kContributions'] += round(roth401kTotal, 2)
    accountsContext['401kPersonalContributions'] = accountsContext['401kPersonalContributions'] - accountsContext['401kContributions_Personal']
    updateSpreadsheet(spreadsheet, '401k Contributions Personal', date, accountsContext['401kPersonalContributions'], 'Personal', 'YTD')
    updateSpreadsheet(spreadsheet, 'Roth 401k Contributions', date, accountsContext['Roth401kContributions'], 'Personal', 'YTD')
    updateSpreadsheet(spreadsheet, 'HSA Contributions Personal', date, accountsContext['HSAPersonalContributions'], 'Personal', 'YTD')
    updateSpreadsheet(spreadsheet, 'IRA Contributions', date, accountsContext['IRAContributions'], 'Personal', 'YTD')
    updateSpreadsheet(spreadsheet, 'Roth IRA Contributions', date, accountsContext['RothIRAContributions'], 'Personal', 'YTD')
    updateSpreadsheet(spreadsheet, 'Brokerage Contributions', date, accountsContext['BrokerageContributions'], 'Personal', 'YTD')
    
def getContributionsForCryptoCurrency(mybook, transactions, accountsContext, date, spreadsheet):
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
    updateSpreadsheet(spreadsheet, 'Crypto Contributions', date, accountsContext['CryptoContributions'], 'Personal', 'YTD')

def getAssetAccountBalances(date, accountList, book, accountsType, timeframe, spreadsheet):
    for account in accountList:
        value = float(book.getGnuAccountBalance(book.getGnuAccountFullName(account), date))
        # if account == 'Brokerage':
        #     value += float(book.getGnuAccountBalance(book.getGnuAccountFullName('GME'), date) * book.getPriceInGnucash('GME'))
        updateSpreadsheet(spreadsheet, account, date, round(value,2), accountsType, timeframe)

def getCellForMonthly(account, month, spreadsheet, accounts='Personal'):
    row = str(spreadsheet.rowStart + (month - 1))
    match account:
        case 'Amazon':                  return 'C' + row if accounts == 'Personal' else 'B' + row
        case 'Bars & Restaurants':      return 'D' + row if accounts == 'Personal' else 'C' + row
        case 'Entertainment':           return 'E' + row if accounts == 'Personal' else 'D' + row
        case 'Other':                   return 'G' + row if accounts == 'Personal' else 'J' + row    
        # Personal
        case 'Joint Expenses':          return 'F' + row
        case 'Dividends':               return 'L' + row
        case 'Interest':                return 'M' + row
        case 'Market Change':           return 'N' + row
        case 'Market Research':         return 'O' + row
        case 'Premiums':                return 'P' + row
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
        
def getCellForYTD(account, spreadsheet, accountsType):
    column = spreadsheet.currentYearColumn
    match account:
        # Update Year % column:
        case 'PercentColumn':                   return chr(ord(column) + 1) + str(1)
        # Joint and Personal
        case 'Amazon':                          return column + str(25) if accountsType == 'Personal' else column + str(7)
        case 'Bars & Restaurants':              return column + str(27) if accountsType == 'Personal' else column + str(8)
        case 'Entertainment':                   return column + str(29) if accountsType == 'Personal' else column + str(9)
        case 'Groceries':                       return column + str(30) if accountsType == 'Personal' else column + str(10)
        case 'Other':                           return column + str(34) if accountsType == 'Personal' else column + str(15)
        # Personal
        # Employer Contributions
        case '401k Contributions':              return column + str(2)
        case 'Dividends':                       return column + str(3)
        case 'HSA Contributions':               return column + str(4)
        case 'Interest':                        return column + str(5)
        case 'Market Change':                   return column + str(6)
        case 'Market Research':                 return column + str(7)
        case 'Pension Contributions':           return column + str(8)   
        case 'Premiums':                        return column + str(9)
        case 'Salary':                          return column + str(10)
        # Personal Contributions
        case '401k Contributions Personal':     return column + str(14)
        case 'Brokerage Contributions':         return column + str(15) 
        case 'Crypto Contributions':            return column + str(16)
        case 'HSA Contributions Personal':      return column + str(17)
        case 'I Bonds':                         return column + str(18)
        case 'IRA Contributions':               return column + str(19)
        case 'Roth 401k Contributions':         return column + str(20)
        case 'Roth IRA Contributions':          return column + str(21)
        # Personal Expenses
        case 'Bank Fees':                       return column + str(26)
        case 'Clothing/Apparel':                return column + str(28)
        case 'Income Taxes':                    return column + str(31)
        case 'Joint Expenses':                  return column + str(32)
        case 'Medical':                         return column + str(33)
        case 'Loan Interest':                   return column + str(35) 
        case 'Loan Principle':                  return column + str(36)         
        case 'Transportation':                  return column + str(37)
        # Asset Accounts
        case 'Vanguard401k':                    return column + str(67)
        case 'Brokerage':                       return column + str(68)
        case 'CryptoCurrency':                  return column + str(69)
        case 'HSA':                             return column + str(70)
        case 'I Bonds':                         return column + str(71)
        case 'IRA':                             return column + str(72)
        case 'Liquid Assets':                   return column + str(73)
        case 'Pension':                         return column + str(74)
        case 'Roth IRA':                        return column + str(75)
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

def updateSpreadsheet(spreadsheet, account, date, value, accountsType, timeframe):
    cell = getCellForMonthly(account, date.month, spreadsheet, accountsType) if timeframe == 'Month' else getCellForYTD(account, spreadsheet, accountsType)
    spreadsheet.writeCell(cell, value)

def runUpdateGoals(accountsType, book):
    driver = Driver("Chrome")
    if accountsType == 'Personal':
        sheetTitle = 'Finances'
        tabTitle = 'Goals'
    else:
        sheetTitle = 'Home'
        tabTitle = 'Finances'
    Goals = Spreadsheet(sheetTitle, tabTitle, driver)
    ytdDateRange = getStartAndEndOfDateRange(timeSpan='YTD')
    lastMonthDateRange = getStartAndEndOfDateRange(timeSpan='Month')
    ytdTransactions = book.getTransactionsByDateRange(ytdDateRange)
    lastMonthTransactions = book.getTransactionsByDateRange(lastMonthDateRange, transactionsToFilter=ytdTransactions)
    ytdAccounts, monthlyAccounts = [], []
    accountsContext = {}
    commonExpenseAccounts = ['Amazon', 'Bars & Restaurants', 'Entertainment', 'Other', 'Groceries']
    ytdAccounts.extend(commonExpenseAccounts)
    monthlyAccounts.extend(commonExpenseAccounts)
    if accountsType == 'Personal':
        specificIncomeAccounts = ['401k Contributions', 'Dividends', 'HSA Contributions', 'Interest', 'Market Change', 'Market Research','Pension Contributions', 'Premiums', 'Salary']
        specificExpenseAccounts = ['Bank Fees', 'Clothing/Apparel', 'Income Taxes', 'Joint Expenses', 'Medical', 'Loan Interest', 'Loan Principle', 'Transportation']
        retirementContributionAccounts = ['Vanguard401k', 'Optum Cash', 'HE Cash', 'FidelityIRASPAXX', 'FidelityRothIRASPAXX', 'FidelityBrokerageSPAXX', 'GME', 'WebullBrokerageCash']
        assetAccounts = ['Vanguard401k', 'Brokerage', 'CryptoCurrency', 'HSA', 'IRA', 'Liquid Assets', 'Pension', 'Roth IRA']
        monthlyAccounts.remove('Groceries')
        monthlyAccounts.extend(['Dividends', 'Interest', 'Joint Expenses', 'Market Change', 'Market Research', 'Premiums'])
    elif accountsType == 'Joint':
        specificIncomeAccounts = ["Dan's Contributions", "Tessa's Contributions"]
        specificExpenseAccounts = ['Home Depot','Home Expenses','Home Furnishings','Pet','Travel','Utilities', 'Mortgage Principle']
        monthlyAccounts.extend(specificIncomeAccounts)
        monthlyAccounts.extend(specificExpenseAccounts)
    ytdAccounts.extend(specificIncomeAccounts); ytdAccounts.extend(specificExpenseAccounts);
    updateSpreadsheet(Goals, 'PercentColumn', lastMonthDateRange['startDate'], float((lastMonthDateRange['startDate'].month/12)), accountsType, 'YTD')
    getTotalForIncomeExpenseAccounts(ytdAccounts, book, ytdTransactions, 'YTD', ytdDateRange['endDate'], accountsContext, accountsType, Goals)
    getTotalForIncomeExpenseAccounts(monthlyAccounts, book, lastMonthTransactions, 'Month', lastMonthDateRange['endDate'], accountsContext, accountsType, Goals)
    if accountsType == 'Personal':
        getContributionsForRetirementAccounts(retirementContributionAccounts, book, ytdTransactions, accountsContext, ytdDateRange['endDate'], Goals)
        getContributionsForCryptoCurrency(book, ytdTransactions, accountsContext, ytdDateRange['endDate'], Goals)
        getAssetAccountBalances(ytdDateRange['endDate'], assetAccounts, book, accountsType, 'YTD', Goals)
    return accountsContext

# if __name__ == '__main__':
    # accounts = 'Joint' # Personal or Joint
    # timeframe = "Month" # Month or YTD
    # book = GnuCash('Finance') if accounts == 'Personal' else GnuCash('Home')
    # runUpdateGoals(accounts, timeframe, book)
    # book.closeBook()


if __name__ == '__main__':
    # from Classes.Asset import USD

    # book = GnuCash('Finance')
    # account =  USD("Vanguard401k", book)
    # dateRange = getStartAndEndOfDateRange(datetime.today().date(), timeSpan='year')
    # transactions = book.getTransactionsByDateRange(dateRange)
    # rothAmount = 0
    # preTaxAmount = 0
    # for tr in transactions:
    #     if 'Paycheck' in tr.description:
    #         print(tr.post_date)
    #         for spl in tr.splits:
    #             if spl.account.fullname == account.gnuAccount:
    #                 if spl.memo == 'roth':
    #                     print('roth')
    #                     print(spl.value)
    #                     rothAmount += spl.value
    #                 elif spl.memo == 'pre-tax':
    #                     print('pre-tax')
    #                     print(spl.value)
    #                     preTaxAmount += spl.value
    # print("rothAmount: " + str(rothAmount))
    # print("preTaxAmount: " + str(preTaxAmount))
    column = 'G'
    print(chr(ord(column) + 1))