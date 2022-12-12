import time

import gspread

from .GeneralFunctions import getCryptocurrencyPrice, setDirectory, showMessage
from .GnuCashFunctions import updateCryptoPriceInGnucash

def updateSpreadsheet(directory, sheetTitle, tabTitle, account, month, value, symbol="$", modified=False):
    def getCell(account, month):
        def getCellArray(account):
            match account:
                ## Asset Allocation Spreadsheet
                case 'Liquid Assets':
                    return ['B6', 'I6', 'P6', 'B28', 'I28', 'P28', 'B50', 'I50', 'P50', 'B72', 'I72', 'P72']
                case 'Bonds':
                    return ['F6', 'M6', 'T6', 'F28', 'M28', 'T28', 'F50', 'M50', 'T50', 'F72', 'M72', 'T72']
                case 'Vanguard401k':
                    return ['B8', 'I8', 'P8', 'B30', 'I30', 'P30', 'B52', 'I52', 'P52', 'B74', 'I74', 'P74']
                case 'VanguardPension':
                    return ['B10', 'I10', 'P10', 'B32', 'I32', 'P32', 'B54', 'I54', 'P54', 'B76', 'I76', 'P76']
                case 'Cryptocurrency':
                    return ['B12', 'I12', 'P12', 'B34', 'I34', 'P34', 'B56', 'I56', 'P56', 'B78', 'I78', 'P78']
                ## Checking Balance Spreadsheet(s)
                #Personal
                case 'BoA':
                    return ['K5', 'S5', 'C40', 'K40', 'S40', 'C75', 'K75', 'S75', 'C110', 'K110', 'S110', 'C5']
                case 'Discover':
                    return ['K6', 'S6', 'C41', 'K41', 'S41', 'C76', 'K76', 'S76', 'C111', 'K111', 'S111', 'C6']             
                case 'Amex':
                    return ['K7', 'S7', 'C42', 'K42', 'S42', 'C77', 'K77', 'S77', 'C112', 'K112', 'S112', 'C7']
                case 'Chase':
                    return ['F8', 'S8', 'C43', 'K43', 'S43', 'C78', 'K78', 'S78', 'C113', 'K113', 'S113', 'C8']            
                case 'Barclays':
                    return ['K9', 'S9', 'C44', 'K44', 'S44', 'C79', 'K79', 'S79', 'C114', 'K114', 'S114', 'C9']
                #Joint
                case 'BoA-joint':
                    return ['K16', 'S16', 'C52', 'K52', 'S52', 'C88', 'K88', 'S88', 'C124', 'K124', 'S124', 'C16']
                ## Cryptocurrency Spreadsheet
                case 'ALGO':
                    return ['H2', 'J2']
                case 'BTC-Midas':
                    return ['H3', 'J3']
                case 'BTC-MyConstant':
                    return ['H4', 'J4']            
                case 'ADA':
                    return ['H5', 'J5']            
                case 'ATOM':
                    return ['H6', 'J6']
                case 'ETH-Midas':
                    return ['H7', 'J7']
                case 'ETH-MyConstant':
                    return ['H8', 'J8']            
                case 'ETH-Kraken':
                    return ['H9', 'J9']
                case 'ETH2':
                    return ['H10', 'J10']
                case 'IOTX':
                    return ['H11', 'J11']
                case 'LRC':
                    return ['H12', 'J12'] 
                case 'DOT':
                    return ['H13', 'J13']          
                case 'PRE':
                    return ['H14', 'J14']

        cell = (getCellArray(account))[month - 1]
        return cell
    def getSheetKey(sheetTitle, tabTitle, worksheet, cellToUpdate):
        if sheetTitle == "Asset Allocation":
            if tabTitle == "Cryptocurrency":
                keyColumn = "B"
            else:
                keyColumn = "A"
        elif sheetTitle == "Checking Balance":
            keyColumn = "B"
        elif sheetTitle == "Home":
            if tabTitle == "Finances":
                keyColumn = "A"
            else:
                keyColumn = "B"
        worksheetKey = worksheet.acell(keyColumn + cellToUpdate[1:]).value
        return worksheetKey
    
    jsonCreds = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open(sheetTitle)
    worksheet = sheet.worksheet(str(tabTitle))
    cell = getCell(account, month)
    if modified:
        cell = cell.replace(cell[0], chr(ord(cell[0]) + 3))
    sheetKey = getSheetKey(sheetTitle, tabTitle, worksheet, cell)
    if symbol == "$" or symbol == sheetKey:
        worksheet.update(cell, value)
    else:
        showMessage('Key Mismatch',     
        f'the given key: {symbol} does not match the sheet key: {sheetKey} for the cell that is being updated: {cell} \n'
        f'This is likely due to an update on the spreadsheet: {sheetTitle} > {tabTitle} \n'
        f'Check spreadsheet and verify the getCell method is getting the correct Cell')

def updateCryptoPrices(driver):
    print('updating coin prices')
    url = "https://docs.google.com/spreadsheets/d/1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/edit#gid=623829469"
    found = driver.findWindowByUrl(url)
    driver = driver.webDriver
    if not found:
        driver.execute_script("window.open('" + url + "');")
        driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    else:
        driver.switch_to.window(found)
        time.sleep(1)
    coinNames = []
    coinSymbols = []
    # capture coin names and symbols from spreadsheet into arrays
    directory = setDirectory()
    jsonCreds = directory + r"\Projects\Coding\Python\FinanceAutomation\Resources\creds.json"
    sheet = gspread.service_account(filename=jsonCreds).open('Asset Allocation')
    worksheet = sheet.worksheet(str('Cryptocurrency'))
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
            if coinName == 'eth2':
                coinName = 'ethereum'
                coinSymbol = 'ETH'
            coinNames.append(coinName)
            coinSymbols.append(coinSymbol)
            row += 1
        else:
            stillCoins = False
    # get prices from coingecko in a single call
    coinPrices = getCryptocurrencyPrice(coinNames)
    # update coin prices in Gnucash and spreadsheet
    for coin in coinNames:
        i = coinNames.index(coin)
        symbol = coinSymbols[i]
        price = format(coinPrices[coin]["usd"], ".2f")
        updateCryptoPriceInGnucash(symbol, price)
        worksheet.update((priceColumn + str(i + 2)), float(price))

def openSpreadsheet(driver, sheet, tab=''):
    url = 'https://docs.google.com/spreadsheets/d/'
    if sheet == 'Checking Balance':
        url += '1684fQ-gW5A0uOf7s45p9tC4GiEE5s5_fjO5E7dgVI1s/'
        if tab == '2022':
            url += 'edit#gid=382679207'
    elif sheet == 'Asset Allocation':
        url += '1sWJuxtYI-fJ6bUHBWHZTQwcggd30RcOSTMlqIzd1BBo/'
        if tab == '2022':
            url += 'edit#gid=2058576150'
        elif tab == 'Goals':
            url += 'edit#gid=1813404638'            
        elif tab == 'Cryptocurrency':
            url += 'edit#gid=623829469'
    elif sheet == 'Home':
        url += '1oP3U7y8qywvXG9U_zYXgjFfqHrCyPtUDl4zPDftFCdM/'
        if tab == '2022 Balance':
            url += 'edit#gid=317262693'
        elif tab == '2023 Balance':
            url += 'edit#gid=14744444'            
        elif tab == 'Finances':
            url += 'edit#gid=1436385671'
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    driver.get(url)