from ibapi.contract import *

class Tickers:
    tickerId = 0
    bid = 0
    ask = 0
    ltp = 0
    objContract = Contract() #IB contract
    bars_data = {} #dictionary to collect 5 seconds data