import os

if __name__ == '__main__' or __name__ == "Ledger":
    from Classes.Asset import Security
    from Classes.GnuCash import GnuCash
    from Functions.GeneralFunctions import showMessage, isProcessRunning
else:
    from .Classes.Asset import Security
    from .Classes.GnuCash import GnuCash
    from .Functions.GeneralFunctions import showMessage, isProcessRunning

def getLedgerAccounts(readBook):
    Bitcoin = Security("Bitcoin", readBook)
    Ethereum = Security("Ethereum", readBook)
    Cosmos = Security("Cosmos", readBook)
    Polkadot = Security("Polkadot", readBook)
    Algorand = Security("Algorand", readBook)
    XRP = Security("Ripple", readBook)
    return [Bitcoin, Ethereum, Cosmos, Polkadot, Algorand, XRP]

def updateCoin(coin, book):
    balance = float(input(f"Paste {coin.symbol} balance here: "))
    coin.setBalance(balance)
    coin.setPrice(coin.getPriceFromCoinGecko())
    coin.updateSpreadsheetAndGnuCash(book)
    
def runLedger(coinList, book):
    if not (isProcessRunning('Ledger Live.exe')):   os.startfile(r'C:\Program Files\Ledger Live\Ledger Live.exe')
    showMessage('Open Ledger and Verify Balances', "click OK and follow prompts")
    for coin in coinList:   updateCoin(coin, book)

# if __name__ == '__main__':
#     book = GnuCash('Finance')    
#     coinList = getLedgerAccounts(book)
#     runLedger(coinList, book)
#     for coin in coinList:
#         coin.getData()
#     book.closeBook()


if __name__ == '__main__':
    # book = GnuCash('Finance')
    # gnuAccount = 'Assets:Non-Liquid Assets:CryptoCurrency'
    # from datetime import datetime
    # date = date=datetime.today().date().replace(month=3, day=31)
    # print(book.getBalance(gnuAccount, date))

    from Functions.GeneralFunctions import getStartAndEndOfDateRange, getPaycheckDates
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    if datetime.today().weekday() == 5:
        print('yes')

    print(datetime.today().weekday())
    # print(getStartAndEndOfDateRange(datetime.today().date()+relativedelta(months=+1), 'month'))
    
    # def eventsHappening(date):
    #     events, monthDates = [], getStartAndEndOfDateRange(date+relativedelta(months=+1), 'month')
    #     if date.day == monthDates['endDate'].day:           events.append('Paycheck')
    #     if date in getPaycheckDates():                      events.append('Paycheck')
    #     if date.month in [2, 5, 8, 11] and date.day == 22:  events.append('Pay Water Bill')
    #     match date.day:
    #         case 1:         events.append('Pay Jon')
    #         case 3:         events.append('Ally Interest')
    #         case 5:         events.append('WE Energies')
    #         case 13:        events.append('BoA-Joint CC Bill posts')
    #         case 14:        events.append('Mortgage Bill')            
    #         case 15:        events.append('Paycheck')
    #         case 17:        events.append('Schedule Ally transfer')
    #         case 24:        events.append('Utility Bill posts')
    #         case _:         return events
    #     return events
    # print(eventsHappening(datetime.today().date().replace(day=22)))