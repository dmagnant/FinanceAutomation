import time, gspread
from json import JSONDecodeError
from datetime import datetime
from .GeneralFunctions import getCryptocurrencyPrice, setDirectory, showMessage, getStockPrice

def updateSpreadsheet(sheetTitle, tabTitle, account, month, value, symbol="$", modifiedCC=False):
    def getCell(account, month, sheet):
        sharesColumn = sheet['sharesColumn']
        priceColumn = sheet['priceColumn']
        def getCellArray(account):
            match account:
                #Joint
                case 'BoA-joint':   return ['K16', 'S16', 'C52', 'K52', 'S52', 'C88', 'K88', 'S88', 'C124', 'K124', 'S124', 'C16']
                case 'Energy Bill': return ['F27', 'N27', 'V27', 'F63', 'N63', 'V63', 'F99', 'N99', 'V99', 'F135', 'N135', 'V135']
                case 'Water Bill':  return ['F25', 'N25', 'V25', 'F61', 'N61', 'V61', 'F97', 'N97', 'V97', 'F133', 'N133', 'V133']
                case 'Mortgage':    return ['F17', 'N17', 'V17', 'F53', 'N53', 'V53', 'F89', 'N89', 'V89', 'F125', 'N125', 'V125']
                ## Cryptocurrency
                case 'BTC':         return [sharesColumn+'2', priceColumn+'2']
                case 'ADA-Eternl':  return [sharesColumn+'3', priceColumn+'3']
                case 'ADA-Nami':    return [sharesColumn+'4', priceColumn+'4']
                case 'ETH':         return [sharesColumn+'5', priceColumn+'5']
                case 'IOTX':        return [sharesColumn+'6', priceColumn+'6']
                case 'PRE':         return [sharesColumn+'7', priceColumn+'7']
                ## Checking Balance Spreadsheet(s)
                case 'BoA':         return ['K5', 'S5', 'C40', 'K40', 'S40', 'C75', 'K75', 'S75', 'C110', 'K110', 'S110', 'C5']
                case 'Discover':    return ['K6', 'S6', 'C41', 'K41', 'S41', 'C76', 'K76', 'S76', 'C111', 'K111', 'S111', 'C6']             
                case 'Amex':        return ['K7', 'S7', 'C42', 'K42', 'S42', 'C77', 'K77', 'S77', 'C112', 'K112', 'S112', 'C7']
                case 'Chase':       return ['F8', 'S8', 'C43', 'K43', 'S43', 'C78', 'K78', 'S78', 'C113', 'K113', 'S113', 'C8']            
                case 'Barclays':    return ['K4', 'S4', 'C39', 'K39', 'S39', 'C74', 'K74', 'S74', 'C109', 'K109', 'S109', 'C4']                
                case _:             print(f'account: {account} not found in "updateSpreadsheet" function')
        cell = (getCellArray(account))[month - 1]
        return cell
    def getSheetKey(sheetTitle, tabTitle, worksheet, cellToUpdate):
        keyColumn = "A" if sheetTitle == "Home" and tabTitle == "Finances" else "B"
        worksheetKey = worksheet.acell(keyColumn + cellToUpdate[1:]).value
        return worksheetKey
    sheet = getInvestmentsSpreadsheetDetails(False)
    cell = getCell(account, month, sheet)
    sheetKey = getSheetKey(sheetTitle, tabTitle, sheet['worksheet'], cell)
    if symbol == "$" or symbol == sheetKey: 
        sheet['worksheet'].update_acell(cell, value)
        if modifiedCC: sheet['worksheet'].update_acell(cell.replace(cell[0], chr(ord(cell[0]) + 3)), value)
        if account == 'Water Bill':
            sheet['worksheet'].update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 1)), account)
            sheet['worksheet'].update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 4)), '')
        if account == 'Mortgage':
            sheet['worksheet'].update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 1)), account)
            sheet['worksheet'].update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 4)), '')            
    else:
        showMessage('Key Mismatch',     
        f'the given key: {symbol} does not match the sheet key: {sheetKey} for the cell that is being updated: {cell} \n'
        f'This is likely due to an update on the spreadsheet: {sheetTitle} > {tabTitle} \n'
        f'Check spreadsheet and verify the getCell method is getting the correct Cell')

def updateCheckingBalanceSpreadsheet(sheetTitle, tabTitle, accountName, month, value):
    projectedRows = [3,3,38,38,38,73,73,73,108,108,108,3]
    projectedColumns = ['J','R','B','J','R','B','J','R','B','J','R','B']
    row=projectedRows[month-1]
    column=projectedColumns[month-1]
    jsonCreds = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheet = sheet.worksheet(str(tabTitle))
    cellNotFound = True
    while cellNotFound:
        description = worksheet.acell(column+str(row)).value
        if description and accountName in description:
                cellNotFound = False
        else:   row+=1
    worksheet.update_acell(chr(ord(column) + 1) + str(row), value)
    worksheet.update_acell(chr(ord(column) + 4) + str(row), value)

def getMortgageSpreadSheetDetails(driver=False):
    if driver:
        spreadsheetWindow = driver.findWindowByUrl("gid=1692958526")
        if not spreadsheetWindow:   openSpreadsheet(driver, 'Mortgage', 'Mortgage'); spreadsheetWindow = driver.webDriver.current_window_handle
        else:   driver.webDriver.switch_to.window(spreadsheetWindow)
    worksheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Mortgage').worksheet('Mortgage')
    return {'worksheet': worksheet, 'firstRowOfThisYear': 79, 'interestColumn':'E', 'dateColumn':'B'}
 
def getInvestmentsSpreadsheetDetails(driver=False):
    if driver:
        spreadsheetWindow = driver.findWindowByUrl("gid=361024172")
        if not spreadsheetWindow:   openSpreadsheet(driver, 'Finances', 'Investments'); spreadsheetWindow = driver.webDriver.current_window_handle
        else:   driver.webDriver.switch_to.window(spreadsheetWindow)
    worksheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Finances').worksheet('Investments')
    return {'worksheet': worksheet, 'row': 2, 'firstRowAfterCrypto':8, 'nameColumn': 'A','symbolColumn': 'B', 'bankColumn': 'C', 'accountColumn': 'D', 'sharesColumn': 'E', 'priceColumn': 'F', 'costColumn':'G', 'profitLossColumn':'I'}

def updateInvestmentsDaily(driver, book, accounts):
    spreadsheet = getInvestmentsSpreadsheetDetails(driver)
    symbolsWithPricesUpdated = ['SPAXX', 'Options']
    symbolsToAvoid = ['8585', 'M038']
    coinsToUpdate = {}
    stillInvestments = True
    row = spreadsheet['row']
    num = 1
    while stillInvestments:
        symbol = spreadsheet['worksheet'].acell(spreadsheet['symbolColumn']+str(row)).value
        if symbol != None:
            if symbol in symbolsToAvoid:
                row+=1
                continue
            else:
                while True:
                    try:
                        account = spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value
                        break
                    except JSONDecodeError: num+=1
            if account == "Crypto":
                coinName = spreadsheet['worksheet'].acell(spreadsheet['nameColumn']+str(row)).value.lower()
                if coinName not in list(coinsToUpdate.keys()):  coinsToUpdate[coinName] = {'symbol': symbol, 'row': row}
            elif account in ['Brokerage', 'rIRA', 'IRA']:
                updateFidelityInvestments(symbol, symbolsWithPricesUpdated, account, accounts['Fidelity'], book, spreadsheet, row)
            else:
                if symbol not in symbolsWithPricesUpdated:
                    price = getStockPrice(symbol)
                    book.updatePriceInGnucash(symbol, price)
                    spreadsheet['worksheet'].update_acell(spreadsheet['priceColumn'] + str(row), float(price))
                    symbolsWithPricesUpdated.append(symbol)
            row += 1
        else:
            if 'Savings' == spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value:
                spreadsheet['worksheet'].update_acell(spreadsheet['sharesColumn']+str(row), float(book.getGnuAccountBalance(accounts['Sofi']['Savings'].gnuAccount)))
            stillInvestments = False
    coinPrices = getCryptocurrencyPrice(list(coinsToUpdate.keys()))     # get prices from coingecko in a single call
    for coin in list(coinsToUpdate.keys()):
        price = format(coinPrices[coin]["usd"], ".2f")
        book.updatePriceInGnucash(coinsToUpdate.get(coin).get('symbol'), price)
        spreadsheet['worksheet'].update_acell((spreadsheet['priceColumn'] + str(coinsToUpdate.get(coin).get('row'))), float(price))

def updateFidelityInvestments(symbol, symbolsWithPricesUpdated, accountID, accounts, book, spreadsheet, row):
    if symbol not in symbolsWithPricesUpdated:
        price = getStockPrice(symbol)
        book.updatePriceInGnucash(symbol, price)
        spreadsheet['worksheet'].update_acell(spreadsheet['priceColumn'] + str(row), float(price))
        symbolsWithPricesUpdated.append(symbol)
    # if accountID == 'Brokerage':  accountPrefix = 'Brokerage'
    # elif accountID == 'rIRA':     accountPrefix = 'rIRA'
    # elif accountID == 'IRA':      accountPrefix = 'IRA'
    account = accounts[accountID + symbol]
    if account.balance:  spreadsheet['worksheet'].update_acell(spreadsheet.get('sharesColumn') + str(row), float(account.balance))
    if account.cost:    spreadsheet['worksheet'].update_acell(spreadsheet.get('costColumn') + str(row), float(account.cost))

def updateInvestmentsMonthly(driver, book, accounts):
    today, stillInvestments, spreadsheet = datetime.today().date(), True, getInvestmentsSpreadsheetDetails(driver)
    row = spreadsheet['firstRowAfterCrypto']
    banksToUpdate = ['Vanguard', 'Health Equity', 'Optum', 'Pension']
    while stillInvestments:
        shares = cost = 0
        bank = spreadsheet['worksheet'].acell(spreadsheet['bankColumn']+str(row)).value
        if bank in banksToUpdate:
            symbol = spreadsheet['worksheet'].acell(spreadsheet['symbolColumn']+str(row)).value
            if symbol == '8585':
                price = book.getPriceInGnucash(accounts['Vanguard']['TSM401k'].symbol, today)
                shares = float(accounts['Vanguard']['TSM401k'].balance)
                cost = float(accounts['Vanguard']['TSM401k'].cost)
            elif symbol == 'M038':
                price = book.getPriceInGnucash(accounts['Vanguard']['EBI'].symbol, today)
                shares = float(accounts['Vanguard']['EBI'].balance)
                cost = float(accounts['Vanguard']['EBI'].cost)
            elif symbol == 'VFIAX':
                price = book.getPriceInGnucash(symbol, today)
                shares = float(accounts['Optum'][symbol].balance)
                cost = book.getDollarsInvestedPerSecurity(accounts['Optum'][symbol])
            elif symbol == 'VIIIX':
                price = book.getPriceInGnucash(symbol, today)
                shares = float(accounts['HealthEquity'][symbol].balance)
                if cost:
                    cost = float(accounts['HealthEquity'][symbol].cost)
            elif bank == 'Pension':
                spreadsheet['worksheet'].update_acell(spreadsheet['sharesColumn']+str(row), float(book.getGnuAccountBalance(accounts['Pension'])))
                spreadsheet['worksheet'].update_acell(spreadsheet['costColumn'] + str(row), float(accounts['Pension'].cost))
            elif bank == 'Sofi':
                spreadsheet['worksheet'].update_acell(spreadsheet['costColumn'] + str(row), float(accounts['Savings'].cost))
            if shares:  spreadsheet['worksheet'].update_acell(spreadsheet['sharesColumn'] + str(row), shares)
            if cost:    spreadsheet['worksheet'].update_acell(spreadsheet['costColumn'] + str(row), cost)
            if price:   spreadsheet['worksheet'].update_acell(spreadsheet['priceColumn'] + str(row), float(price))
            row += 1
        else:   stillInvestments = False

def getSheetGIDSuffix(sheet, tab=''):
    GID = 0
    if sheet == 'Finances':
        if tab == 'Goals':              GID='1813404638'            
        elif tab == 'Investments':      GID= '361024172'
        if tab == '2024':               GID= '113072953'
    elif sheet == 'Home':
        if tab == '2024 Balance':       GID= '565871395'
        elif tab == 'Finances':         GID= '1436385671'
    elif sheet == 'Mortgage':
        if tab == 'Mortgage':           GID='1692958526'
    return f'edit?gid={GID}#gid={GID}'

def openSpreadsheet(driver, sheet, tab=''):
    url = 'https://docs.google.com/spreadsheets/d/'
    if sheet == 'Finances':
        url += '1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/'
        if tab == 'Goals':              
            url += 'edit#gid=1813404638'            
        elif tab == 'Investments':      url += getSheetGIDSuffix(sheet, tab)
        if tab == '2024':               url += getSheetGIDSuffix(sheet, tab)
    elif sheet == 'Home':
        url += '1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/'
        if tab == '2024 Balance':       url += getSheetGIDSuffix(sheet, tab)
        elif tab == 'Finances':         url += getSheetGIDSuffix(sheet, tab)
    elif sheet == 'Mortgage':
        url += '1uzX0Wn0xSHzJAwf4M_xsG8AkFMK_iClYxRYBv7NP4OQ/edit?gid=1692958526/'
        if tab == 'Mortgage':           url += getSheetGIDSuffix(sheet, tab)
    if not driver.findWindowByUrl(url): driver.openNewWindow(url)