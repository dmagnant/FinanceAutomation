import time, gspread
from datetime import datetime
from .GeneralFunctions import getCryptocurrencyPrice, setDirectory, showMessage, getStockPrice

def updateSpreadsheet(sheetTitle, tabTitle, account, month, value, symbol="$", modifiedCC=False):
    def getCell(account, month):
        def getCellArray(account):
            match account:
                #Joint
                case 'BoA-joint':   return ['K16', 'S16', 'C52', 'K52', 'S52', 'C88', 'K88', 'S88', 'C124', 'K124', 'S124', 'C16']
                case 'Energy Bill': return ['F27', 'N27', 'V27', 'F63', 'N63', 'V63', 'F99', 'N99', 'V99', 'F135', 'N135', 'V135']
                case 'Water Bill':  return ['F25', 'N25', 'V25', 'F61', 'N61', 'V61', 'F97', 'N97', 'V97', 'F133', 'N133', 'V133']
                ## Cryptocurrency
                case 'BTC':         return ['D2', 'E2']
                case 'ADA-Eternl':  return ['D3', 'E3']
                case 'ADA-Nami':    return ['D4', 'E4']
                case 'ETH':         return ['D5', 'E5']
                case 'IOTX':        return ['D6', 'E6']
                case 'PRE':         return ['D7', 'E7']
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
        # if sheetTitle == "Asset Allocation":    keyColumn = "B"
        # elif sheetTitle == "Checking Balance":  keyColumn = "B"
        # elif sheetTitle == "Home":              keyColumn = "A" if tabTitle == "Finances" else "B"
        worksheetKey = worksheet.acell(keyColumn + cellToUpdate[1:]).value
        return worksheetKey
    
    jsonCreds = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheet = sheet.worksheet(str(tabTitle))
    cell = getCell(account, month)
    sheetKey = getSheetKey(sheetTitle, tabTitle, worksheet, cell)
    if symbol == "$" or symbol == sheetKey: 
        worksheet.update_acell(cell, value)
        if modifiedCC: worksheet.update_acell(cell.replace(cell[0], chr(ord(cell[0]) + 3)), value)
        if account == 'Water Bill': 
            worksheet.update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 1)), account)
            worksheet.update_acell(cell.replace(cell[0], chr(ord(cell[0]) - 4)), '')
    else:
        showMessage('Key Mismatch',     
        f'the given key: {symbol} does not match the sheet key: {sheetKey} for the cell that is being updated: {cell} \n'
        f'This is likely due to an update on the spreadsheet: {sheetTitle} > {tabTitle} \n'
        f'Check spreadsheet and verify the getCell method is getting the correct Cell')

def updateCheckingBalanceSpreadsheet(sheetTitle, tabTitle, accountName, month, value):
    projectedRows = [4,4,39,39,39,74,74,74,109,109,109,4]
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
        if accountName in description:  cellNotFound = False
        else:   row+=1
    worksheet.update_acell(chr(ord(column) + 1) + str(row), value)
    worksheet.update_acell(chr(ord(column) + 4) + str(row), value)

def getInvestmentsSpreadsheetDetails(driver):
    spreadsheetWindow = driver.findWindowByUrl("edit#gid=361024172")
    if not spreadsheetWindow:   openSpreadsheet(driver, 'Finances', 'Investments'); spreadsheetWindow = driver.webDriver.current_window_handle
    else:   driver.webDriver.switch_to.window(spreadsheetWindow)
    worksheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Finances').worksheet('Investments')
    return {'worksheet': worksheet, 'row': 2, 'firstRowAfterCrypto':8, 'nameColumn': 'A','symbolColumn': 'B', 'accountColumn': 'C', 'sharesColumn': 'D', 'priceColumn': 'E', 'costColumn': 'F', 'profitLossColumn':'H'}

def updateInvestmentsDaily(driver, book):
    spreadsheet = getInvestmentsSpreadsheetDetails(driver)
    symbolsToUpdate = ['GME', 'VIIIX', 'VXUS', 'VTI', 'VFIAX']
    coinsToUpdate = {}
    stillInvestments = True
    row = spreadsheet['row']
    while stillInvestments:
        symbol = spreadsheet['worksheet'].acell(spreadsheet['symbolColumn']+str(row)).value
        if symbol != None:
            if symbol in symbolsToUpdate:
                price = getStockPrice(symbol)
                book.updatePriceInGnucash(symbol, price)
                spreadsheet['worksheet'].update_acell(spreadsheet['priceColumn'] + str(row), float(price))
                symbolsToUpdate.remove(symbol)
            elif spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value == "Crypto":
                coinName = spreadsheet['worksheet'].acell(spreadsheet['nameColumn']+str(row)).value.lower()
                if coinName not in list(coinsToUpdate.keys()):  coinsToUpdate[coinName] = {'symbol': symbol, 'row': row}
            elif symbol == 'Options': 
                row+=1
                continue
            row += 1
        else:          
            stillInvestments = False
    coinPrices = getCryptocurrencyPrice(list(coinsToUpdate.keys()))     # get prices from coingecko in a single call
    for coin in list(coinsToUpdate.keys()):
        price = format(coinPrices[coin]["usd"], ".2f")
        book.updatePriceInGnucash(coinsToUpdate.get(coin).get('symbol'), price)
        spreadsheet['worksheet'].update_acell((spreadsheet['priceColumn'] + str(coinsToUpdate.get(coin).get('row'))), float(price))

def updateInvestmentsDailyAmended(driver, book, accounts):
    spreadsheet = getInvestmentsSpreadsheetDetails(driver)
    symbolsWithPricesUpdated = ['SPAXX', 'Options']
    symbolsToAvoid = ['8585', 'M038']
    coinsToUpdate = {}
    stillInvestments = True
    row = spreadsheet['row']
    while stillInvestments:
        symbol = spreadsheet['worksheet'].acell(spreadsheet['symbolColumn']+str(row)).value
        if symbol != None:
            if symbol in symbolsToAvoid:
                row+=1
                continue
            else:
                account = spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value
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
    if accountID == 'Brokerage':  accountPrefix = 'br'
    elif accountID == 'rIRA':     accountPrefix = 'rira'
    elif accountID == 'IRA':      accountPrefix = 'ira'
    account = accounts[accountPrefix + symbol]
    if account.balance:  spreadsheet['worksheet'].update_acell(spreadsheet.get('sharesColumn') + str(row), float(account.balance))
    if account.cost:    spreadsheet['worksheet'].update_acell(spreadsheet.get('costColumn') + str(row), float(account.cost))

def updateInvestmentsMonthly(driver, book, accounts):
    today, stillInvestments, spreadsheet = datetime.today().date(), True, getInvestmentsSpreadsheetDetails(driver)
    row = spreadsheet['firstRowAfterCrypto']
    accountsToUpdate = ['401k', 'HSA-HE', 'HSA-O', 'Pension']
    while stillInvestments:
        spreadsheet['priceColumn'] = 'E'
        shares = cost = 0
        account = spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value
        if account in accountsToUpdate:
            symbol = spreadsheet['worksheet'].acell(spreadsheet['symbolColumn']+str(row)).value
            if symbol == '8585':
                price = book.getPriceInGnucash(accounts['TSM401k'].symbol, today)
                shares = float(accounts['TSM401k'].balance)
                cost = float(accounts['TSM401k'].cost)
            elif symbol == 'M038':
                price = book.getPriceInGnucash(accounts['EBI'].symbol, today)
                shares = float(accounts['EBI'].balance)
                cost = float(accounts['EBI'].cost)
            elif symbol == 'VFIAX':
                price = book.getPriceInGnucash(symbol, today)
                shares = float(accounts[symbol].balance)
                cost = book.getDollarsInvestedPerSecurity(accounts[symbol])
            elif symbol == 'VIIIX':
                price = book.getPriceInGnucash(symbol, today)
                shares = float(accounts[symbol].balance); cost = float(account.cost)
                cost = float(account.cost)
            elif account == 'Pension':
                spreadsheet['worksheet'].update_acell(spreadsheet['sharesColumn']+str(row), float(book.getGnuAccountBalance(accounts['Pension'])))
                spreadsheet['worksheet'].update_acell(spreadsheet['costColumn'] + str(row), float(accounts['Pension'].cost))
            if account == 'Savings':
                spreadsheet['worksheet'].update_acell(spreadsheet['costColumn'] + str(row), float(accounts['Savings'].cost))
            # elif symbol in ['VIIIX', 'VXUS', 'VTI']:
            #     price = book.getPriceInGnucash(symbol, today)
            #     if symbol == 'VTI':
            #         match(spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value):
            #             case 'rIRA':        account = accounts['riraVTI']
            #             case 'IRA':         account = accounts['iraVTI']
            #             case 'Brokerage':   account = accounts['brVTI']
            #         shares = float(account.balance)
            #         cost = float(account.cost)
            #     elif symbol == 'VIIIX': shares = float(accounts['VIIIX'].balance); cost = float(account.cost)
            #     elif symbol == 'VXUS':  shares = float(accounts['riraVXUS'].balance); cost = float(account.cost)
            # elif symbol == 'GME':
            #     match(spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value):
            #         case 'rIRA':        account = accounts['riraGME']
            #         case 'IRA':         account = accounts['iraGME']
            #         case 'Brokerage':   account = accounts['brGME']
            #         case _:             row += 1; continue
            #     price = getStockPrice(symbol)
            #     shares = float(account.balance)
            #     cost = float(account.cost)
            # elif symbol == 'SPAXX':
            #     match(spreadsheet['worksheet'].acell(spreadsheet['accountColumn']+str(row)).value):
            #         case 'rIRA':        account = accounts['riraSPAXX']
            #         case 'IRA':         account = accounts['iraSPAXX']
            #         case 'Brokerage':   account = accounts['brSPAXX']
            #     shares = float(account.balance)
            #     spreadsheet['worksheet'].update_acell(spreadsheet.get('sharesColumn') + str(row), shares)
            #     row += 1
            #     continue
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
    if not driver.findWindowByUrl(url): driver.openNewWindow(url)