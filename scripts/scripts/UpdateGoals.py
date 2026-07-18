import gspread
from datetime import date, datetime

if __name__ == '__main__' or __name__ == "UpdateGoals":
    from Classes.Selenium import WebDriver
    from Classes.GnuCash import GnuCash
    from Classes.Spreadsheet import Spreadsheet

    from Functions.GeneralFunctions import (getStartAndEndOfDateRange,setDirectory, showMessage)
else:
    from .Classes.GnuCash import GnuCash
    from .Classes.Spreadsheet import Spreadsheet
    from .Functions.GeneralFunctions import (getStartAndEndOfDateRange,setDirectory, showMessage)

def getTotalForIncomeExpenseAccounts(accountList, mybook, transactions, timeframe, date, accounts, accountsType, spreadsheet):
    for i in accountList:
        print(i)
        total, readBook = 0, mybook.readBook
        account = readBook.accounts(fullname=mybook.getGnuAccountFullName(i))
        accountsToUpdate = list(mybook.getAccountDescendants(account, isReadOnly=True))
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
        print(f"Total for {i} is: {total} and accountsType is: {accountsType}")
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
                    if "Paycheck" in tr.description or 'Non-Elective Contribution' in tr.description:
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
        if account in ['Optum Cash', 'HE Cash']:                                                            accountsContext['HSAPersonalContributions'] += round(total, 2)
        elif account == 'FidelityIRACash':                                                                  accountsContext['IRAContributions'] += round(total, 2)
        elif account == 'FidelityRothIRACash':                                                              accountsContext['RothIRAContributions'] += round(total, 2)
        elif account in ['FidelityIndividualCash', 'FidelityBusinessCash', 'GME', 'WebullBrokerageCash']:   accountsContext['BrokerageContributions'] += round(total, 2)
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
    
def getContributionsForCryptoCurrency(book, transactions, accountsContext, date, spreadsheet):
    total = book.getCryptoCurrencyDepositsFromExistingTransactions(transactions)
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
        # Personal
        case 'Business Expenses':       return 'C' + row
        case 'Personal Expenses':       return 'D' + row
        case 'Business Income':         return 'I' + row
        case 'Investments':             return 'J' + row
        # Joint
        case 'Amazon':                  return 'B' + row
        case 'Bars & Restaurants':      return 'C' + row
        case 'Cars':                    return 'D' + row
        case 'Entertainment':           return 'E' + row
        case 'Groceries':               return 'F' + row
        case 'Home Depot':              return 'G' + row
        case 'Home Expenses':           return 'H' + row
        case 'Home Furnishings':        return 'I' + row
        case 'Mortgage Principle':      return 'J' + row
        case 'Other':                   return 'K' + row    
        case 'Pet':                     return 'L' + row
        case 'Travel':                  return 'M' + row
        case 'Utilities':               return 'N' + row
        case "Dan's Contributions":     return 'R' + row
        case "Tessa's Contributions":   return 'S' + row
        case _:                         print('Month cell not found for: ' + account)
        
def getCellForYTD(account, spreadsheet, accountsType):
    column = spreadsheet.currentYearColumn
    match account:
        # Update Year % column:
        case 'PercentColumn':                   return chr(ord(column) + 1) + str(1)
        # Personal
        # Income
        case '401k Contributions':              return column + str(2)
        case 'Business Income':                 return column + str(3)
        case 'HSA Contributions':               return column + str(4)
        case 'Interest/Dividends':              return column + str(5)
        case 'Market Change':                   return column + str(6)
        case 'Pension Contributions':           return column + str(7)
        case 'Premiums':                        return column + str(8)   
        case 'Salary':                          return column + str(9)
        # Personal Contributions
        case '401k Contributions Personal':     return column + str(13)
        case 'Brokerage Contributions':         return column + str(14) 
        case 'Crypto Contributions':            return column + str(15)
        case 'HSA Contributions Personal':      return column + str(16)
        case 'I Bonds':                         return column + str(17)
        case 'IRA Contributions':               return column + str(18)
        case 'Roth 401k Contributions':         return column + str(19)
        case 'Roth IRA Contributions':          return column + str(20)
        # Personal Expenses
        case 'Business Expenses':               return column + str(24)
        case 'Income Taxes':                    return column + str(25)
        case 'Joint Expenses':                  return column + str(26)
        case 'Personal Expenses':               return column + str(27)
        # Asset Accounts
        case 'Vanguard401k':                    return column + str(58)
        case 'Brokerage':                       return column + str(59)
        case 'CryptoCurrency':                  return column + str(60)
        case 'HSA':                             return column + str(61)
        case 'I Bonds':                         return column + str(62)
        case 'IRA':                             return column + str(63)
        case 'Liquid Assets':                   return column + str(64)
        case 'Pension':                         return column + str(65)
        case 'VanguardRoth401k':                return column + str(66)
        case 'Roth IRA':                        return column + str(67)
        # Joint
        case "Dan's Contributions":             return column + str(2)                 
        case "Tessa's Contributions":           return column + str(3)
        case 'Amazon':                          return column + str(7)
        case 'Bars & Restaurants':              return column + str(8)
        case 'Cars':                            return column + str(9)
        case 'Entertainment':                   return column + str(10)
        case 'Groceries':                       return column + str(11)                 
        case 'Home Depot':                      return column + str(12)
        case 'Home Expenses':                   return column + str(13)
        case 'Home Furnishings':                return column + str(14)
        case 'Mortgage Principle':              return column + str(15)
        case 'Other':                           return column + str(16)
        case 'Pet':                             return column + str(17)
        case 'Travel':                          return column + str(18)
        case 'Utilities':                       return column + str(19)
        case _:                                 print('YTD cell not found for: ' + account)

def updateSpreadsheet(spreadsheet, account, date, value, accountsType, timeframe):
    cell = getCellForMonthly(account, date.month, spreadsheet, accountsType) if timeframe == 'Month' else getCellForYTD(account, spreadsheet, accountsType)
    spreadsheet.writeCell(cell, value)

def runUpdateGoals(accountsType, book):
    driver = WebDriver("Chrome")
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
    if accountsType == 'Personal':
        specificIncomeAccounts = ['401k Contributions', 'Interest/Dividends', 'HSA Contributions', 'Market Change','Pension Contributions', 'Premiums', 'Salary', 'Business Income']
        specificExpenseAccounts = ['Business Expenses', 'Income Taxes', 'Joint Expenses', 'Personal Expenses']
        retirementContributionAccounts = ['Vanguard401k', 'VanguardRoth401k', 'Optum Cash', 'HE Cash', 'FidelityIRACash', 'FidelityRothIRACash', 'FidelityIndividualCash', 'GME', 'WebullBrokerageCash', 'FidelityBusinessCash', 'CryptoContributions']
        assetAccounts = ['Vanguard401k', 'VanguardRoth401k', 'Brokerage', 'CryptoCurrency', 'HSA', 'IRA', 'Liquid Assets', 'Pension', 'Roth IRA']
        monthlyAccounts.extend(['Business Expenses', 'Personal Expenses', 'Business Income', 'Investments'])
    elif accountsType == 'Joint':
        specificIncomeAccounts = ["Dan's Contributions", "Tessa's Contributions"]
        specificExpenseAccounts = ['Amazon', 'Bars & Restaurants', 'Entertainment', 'Other', 'Groceries', 'Cars', 'Home Depot','Home Expenses','Home Furnishings','Pet','Travel','Utilities', 'Mortgage Principle']
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
    # driver = WebDriver("Chrome")
    book = GnuCash('Finance')
    # account =  USD("Vanguard401k", book)
    dateRange = getStartAndEndOfDateRange(timeSpan="month")
    transactions = book.getTransactionsByDateRange(dateRange)
    # rothAmount = 0
    # preTaxAmount = 0
    # for tr in transactions:
    #     if 'Paycheck' in tr.description or 'Non-Elective Contribution' in tr.description:
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
    # # Finances = Spreadsheet('Finances', 'Investments', driver)
    # # from Monthly import getMonthlyAccounts
    # # accounts = getMonthlyAccounts('Crypto', book, None)
    # # Finances.updateCryptoInvestmentsMonthly(book, accounts)


    timeframe = 'YTD'
    i = 'Business Income'
    # print(i)
    total, readBook = 0, book.readBook
    # accountsToUpdate = [readBook.accounts(fullname=book.getGnuAccountFullName(i))]
    # for acc in accountsToUpdate[0].children:
    #     accountsToUpdate.append(acc)

    # for acc in accountsToUpdate:
    #     print(f'account to update: {acc.fullname}')
    #     for tr in transactions:
    #         for spl in tr.splits:
    #             if spl.account.fullname == acc.fullname:
    #                 if "Income:" in acc.fullname or "'s Contributions" in acc.fullname:     value = -spl.value 
    #                 else:                                                                   value = spl.value
    #                 print(f'value found: {value} for account: {acc.fullname} and transaction: {tr.description}')
    #                 amount = format(value, ".2f")
    #                 total += float(amount)
    # print(f"Total for {i} is: {total} and accountsType is: Personal")

    baseAccount = readBook.accounts(fullname=book.getGnuAccountFullName(i))

    # def getAllAccountDescendants(account):
    #     yield account
    #     for child in account.children:
    #         yield from getAllAccountDescendants(child)

    accountsToUpdate = list(book.getAccountDescendants(baseAccount))
    for i in accountsToUpdate:
        print(i.fullname)