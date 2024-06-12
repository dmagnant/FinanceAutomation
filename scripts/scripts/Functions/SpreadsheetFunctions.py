import time, gspread
from datetime import datetime
from .GeneralFunctions import getCryptocurrencyPrice, setDirectory, showMessage, getStockPrice

def updateSpreadsheet(sheetTitle, tabTitle, account, month, value, symbol="$", modified=False):
    def getCell(account, month):
        def getCellArray(account):
            match account:
                ## Asset Allocation Spreadsheet
                # case 'Liquid Assets':
                #     return ['B6', 'I6', 'P6', 'B26', 'I26', 'P26', 'B46', 'I46', 'P46', 'B66', 'I66', 'P66']
                # case 'Bonds':
                #     return ['F6', 'M6', 'T6', 'F26', 'M26', 'T26', 'F46', 'M46', 'T46', 'F66', 'M66', 'T66']
                # case 'Vanguard401k':
                #     return ['B8', 'I8', 'P8', 'B28', 'I28', 'P28', 'B48', 'I48', 'P48', 'B68', 'I68', 'P68']
                # case 'VanguardPension':
                #     return ['B10', 'I10', 'P10', 'B30', 'I30', 'P30', 'B50', 'I50', 'P50', 'B70', 'I70', 'P70']
                # case 'Crypto':
                #     return ['B12', 'I12', 'P12', 'B32', 'I32', 'P32', 'B52', 'I52', 'P52', 'B72', 'I72', 'P72']
                #Joint
                case 'BoA-joint':
                    return ['K16', 'S16', 'C52', 'K52', 'S52', 'C88', 'K88', 'S88', 'C124', 'K124', 'S124', 'C16']
                case 'Energy Bill':
                    return ['F27', 'N27', 'V27', 'F63', 'N63', 'V63', 'F99', 'N99', 'V99', 'F135', 'N135', 'V135']
                case 'Water Bill':
                    return ['F25', 'N25', 'V25', 'F61', 'N61', 'V61', 'F97', 'N97', 'V97', 'F133', 'N133', 'V133']
                ## Cryptocurrency Spreadsheet
                case 'ALGO':
                    return ['H2', 'J2']
                case 'BTC':
                    return ['H3', 'J3']
                case 'ADA-Eternl':
                    return ['H4', 'J4']
                case 'ADA-Nami':
                    return ['H5', 'J5']
                case 'ATOM':
                    return ['H6', 'J6']
                case 'ETH':
                    return ['H7', 'J7']
                case 'IOTX':
                    return ['H8', 'J8']
                case 'DOT':
                    return ['H9', 'J9']
                case 'PRE':
                    return ['H10', 'J10']
                case 'XRP':
                    return ['H11', 'J11']                
                ## Checking Balance Spreadsheet(s)
                case 'BoA':
                    return ['K5', 'S5', 'C40', 'K40', 'S40', 'C75', 'K75', 'S75', 'C110', 'K110', 'S110', 'C5']
                case 'Discover':
                    return ['K6', 'S6', 'C41', 'K41', 'S41', 'C76', 'K76', 'S76', 'C111', 'K111', 'S111', 'C6']             
                case 'Amex':
                    return ['K7', 'S7', 'C42', 'K42', 'S42', 'C77', 'K77', 'S77', 'C112', 'K112', 'S112', 'C7']
                case 'Chase':
                    return ['F8', 'S8', 'C43', 'K43', 'S43', 'C78', 'K78', 'S78', 'C113', 'K113', 'S113', 'C8']            
                case 'Barclays':
                    return ['K4', 'S4', 'C39', 'K39', 'S39', 'C74', 'K74', 'S74', 'C109', 'K109', 'S109', 'C4']                
                case _:
                    print(f'account: {account} not found in "updateSpreadsheet" function')
        cell = (getCellArray(account))[month - 1]
        return cell
    def getSheetKey(sheetTitle, tabTitle, worksheet, cellToUpdate):
        if sheetTitle == "Asset Allocation":    keyColumn = "B" if tabTitle == "Cryptocurrency" else "A"
        elif sheetTitle == "Checking Balance":  keyColumn = "B"
        elif sheetTitle == "Home":              keyColumn = "A" if tabTitle == "Finances" else "B"
        worksheetKey = worksheet.acell(keyColumn + cellToUpdate[1:]).value
        return worksheetKey
    
    jsonCreds = setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheet = sheet.worksheet(str(tabTitle))
    cell = getCell(account, month)
    if modified: cell = cell.replace(cell[0], chr(ord(cell[0]) + 3))
    sheetKey = getSheetKey(sheetTitle, tabTitle, worksheet, cell)
    if symbol == "$" or symbol == sheetKey: worksheet.update_acell(cell, value)
    else:
        showMessage('Key Mismatch',     
        f'the given key: {symbol} does not match the sheet key: {sheetKey} for the cell that is being updated: {cell} \n'
        f'This is likely due to an update on the spreadsheet: {sheetTitle} > {tabTitle} \n'
        f'Check spreadsheet and verify the getCell method is getting the correct Cell')

def updateCheckingBalanceSpreadsheet(sheetTitle, tabTitle, accountName, month, value, symbol="$", modified=False):
    projectedRows = [4,4,39,39,39,74,74,74,109,109,109,4]
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
    cell = chr(ord(column) + 1) + str(row)
    worksheet.update_acell(cell, value)
    cell = chr(ord(column) + 4) + str(row)
    worksheet.update_acell(cell, value)

def updateCryptoPrices(driver, book):
    print('updating coin prices')
    url = "edit#gid=623829469"
    found = driver.findWindowByUrl(url)
    if not found:   openSpreadsheet(driver, 'Asset Allocation', 'Cryptocurrency')
    else:   driver.webDriver.switch_to.window(found); time.sleep(1)
    coinNames = []
    coinSymbols = []
    sheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Asset Allocation')
    worksheet = sheet.worksheet('Cryptocurrency')
    nameColumn = 'A'
    symbolColumn = 'B'
    priceColumn = 'J'
    row = 2
    stillCoins = True
    while stillCoins:
        coinName = worksheet.acell(nameColumn+str(row)).value
        if coinName != None:
            coinName = coinName.lower()
            coinSymbol = worksheet.acell(symbolColumn+str(row)).value
            coinNames.append(coinName)
            coinSymbols.append(coinSymbol)
            row += 1
        else:   stillCoins = False
    coinPrices = getCryptocurrencyPrice(coinNames)     # get prices from coingecko in a single call
    # update coin prices in Gnucash and spreadsheet
    for coin in coinNames:
        i = coinNames.index(coin)
        symbol = coinSymbols[i]
        price = format(coinPrices[coin]["usd"], ".2f")
        book.updatePriceInGnucash(symbol, price)
        worksheet.update_acell((priceColumn + str(i + 2)), float(price))

def updateInvestmentPricesAndShares(driver, book, accounts):
    today = datetime.today().date()
    print('updating investment prices')
    spreadsheetWindow = driver.findWindowByUrl("edit#gid=361024172")
    if not spreadsheetWindow:   openSpreadsheet(driver, 'Asset Allocation', 'Investments'); spreadsheetWindow = driver.webDriver.current_window_handle
    else:   driver.webDriver.switch_to.window(spreadsheetWindow)
    row = 12  # first row after crypto investments
    symbolColumn = 'B'
    accountColumn = 'C'
    sharesColumn = 'D'
    sheet = gspread.service_account(filename=setDirectory() + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json").open('Asset Allocation')
    worksheet = sheet.worksheet('Investments')
    stillInvestments = True
    while stillInvestments:
        priceColumn = 'E'
        symbol = worksheet.acell(symbolColumn+str(row)).value
        shares = 0
        if symbol != None:
            if symbol == '8585':
                price = book.getPriceInGnucash(accounts['TSM401k'].symbol, today)
                shares = float(accounts['TSM401k'].balance)
            elif symbol == 'M038':
                price = book.getPriceInGnucash(accounts['EBI'].symbol, today)
                shares = float(accounts['EBI'].balance)
            elif symbol in ['VIIIX', 'VXUS', 'VTI']:
                price = book.getPriceInGnucash(symbol, today)
                if symbol == 'VTI':
                    match(worksheet.acell(accountColumn+str(row)).value):
                        case 'rIRA':
                            account = accounts['riraVTI']
                        case 'IRA':
                            account = accounts['iraVTI']
                        case 'Brokerage':
                            account = accounts['brVTI']
                    shares = float(account.balance)
                elif symbol == 'VIIIX': shares = float(accounts['VIIIX'].balance)
                elif symbol == 'VXUS':  shares = float(accounts['riraVXUS'].balance)
            elif symbol == 'SPAXX':
                match(worksheet.acell(accountColumn+str(row)).value):
                    case 'rIRA':
                        account = accounts['riraSPAXX']
                    case 'IRA':
                        account = accounts['iraSPAXX']
                    case 'Brokerage':
                        account = accounts['brSPAXX']
                shares = float(account.balance)
                worksheet.update_acell(sharesColumn + str(row), shares)
                row+=1
                continue
            elif symbol == 'HOME':
                price = (250000 - accounts['Home'].getGnuBalance()) / 2
                priceColumn = 'F'
            else:
                price = getStockPrice(driver, symbol)
                driver.webDriver.switch_to.window(spreadsheetWindow)
            if shares:  worksheet.update_acell(sharesColumn + str(row), shares)
            worksheet.update_acell((priceColumn + str(row)), float(price))
            row += 1
        else:   stillInvestments = False

def openSpreadsheet(driver, sheet, tab=''):
    url = 'https://docs.google.com/spreadsheets/d/'
    if sheet == 'Checking Balance':
        url += '1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/'
        if tab == '2024':               url += 'edit#gid=1934202459'
    elif sheet == 'Asset Allocation':
        url += '1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/'
        if tab == 'Goals':              url += 'edit#gid=1813404638'            
        elif tab == 'Cryptocurrency':   url += 'edit#gid=623829469'
        elif tab == 'Investments':      url += 'edit#gid=361024172'
    elif sheet == 'Home':
        url += '1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/'
        if tab == '2024 Balance':       url += 'edit#gid=565871395'            
        elif tab == 'Finances':         url += 'edit#gid=1436385671'
    driver.openNewWindow(url)