import global_variables
import tickers
import bars
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from threading import Thread
from csv import reader
from ibapi.utils import iswrapper #just for decorator
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
from datetime import datetime
import Log

class Wrapper(EWrapper):
    IB_date_time = ""
    #The wrapper deals with the action coming back from the IB gateway or TWS instance
    #We override methods in EWrapper that will get called when this action happens, like currentTime
    # Extra methods are added as we need to store the results in this object
    def __init__(self):
        try:
            self._my_contract_details = {}
            self._my_market_data_dict = {}
        except Exception as ex:
            Log.WriteLog("ibpython.__init__",ex)
    ## error handling code
    @iswrapper
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        try:
            super().error(reqId, errorCode, errorString)
            print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        except Exception as ex:
            Log.WriteLog("ibpython.error",ex)
    ## get next valid orderId
    @iswrapper
    def nextValidId(self, orderId:int):
        try:
            print(f"next valid orderId: {orderId}")
            Ibpython.read_tickers_csv_file()
        except Exception as ex:
            Log.WriteLog("ibpython.nextValidId",ex)
    @iswrapper #get live bid, ask and last trading prices
    def tickPrice(self, reqId: TickerId , tickType: TickType, price: float, attrib:TickAttrib):
        try:
            self.IB_date_time = datetime.now()
            if reqId in global_variables.GlobalVariables.tickers_dict.keys():
                objTicker = global_variables.GlobalVariables.tickers_dict[reqId]
                if tickType == 1:
                    objTicker.bid = price
                elif tickType == 2:
                    objTicker.ask = price
                elif tickType == 4:
                    objTicker.ltp = price
    
            print(f"TickerId : {objTicker.tickerId} Symbol : {objTicker.symbol} Bid : {objTicker.bid} Ask : {objTicker.ask} LTP : {objTicker.ltp}")
            self.db.Insert(f"insert into DataLive (dt,symbol,securityType,exchange,currency,bid,ask,ltp) values('{self.IB_date_time}','{objTicker.symbol}','{objTicker.objContract.secType}','{objTicker.objContract.exchange}','{objTicker.objContract.currency}',{objTicker.bid},{objTicker.ask},{objTicker.ltp})")
        except Exception as ex:
            Log.WriteLog("ibpython.tickerPrice",ex)
    @iswrapper #get open, high, low, close, volume every 5 seconds
    def realtimeBar(self, reqId: TickerId, time:int, open_: float, high: float, low: float, close: float,volume: int, wap: float, count: int):
        try:
            super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
            if reqId in global_variables.GlobalVariables.tickers_dict.keys():
                objTicker = global_variables.GlobalVariables.tickers_dict[reqId]
    
                objBar = bars.Bars()
                objBar.dt = datetime.fromtimestamp(time)
                objBar.dt = objBar.dt.strftime("%x %X")
                objBar.open = open_
                objBar.high = high
                objBar.low = low
                objBar.close = close
                objBar.volume = volume
                objBar.wap = wap
                objTicker.bars_data[objBar.dt] = objBar
    
            print("RealTimeBar. TickerId:", objTicker.tickerId, objBar.close)
            #insert real time default 5 seconds bars into database
            self.db.Insert(f"insert into DataBars(dt,symbol,securityType,exchange,currency,[open],high,low,[close],volume,wap,timeframe) values('{objBar.dt}','{objTicker.symbol}','{objTicker.objContract.secType}','{objTicker.objContract.exchange}','{objTicker.objContract.currency}',{objBar.open},{objBar.high},{objBar.low},{objBar.close},{objBar.volume},{objBar.wap},'5')")
        except Exception as ex:
            Log.WriteLog("ibpython.realtimeBar",ex)
class Client(EClient):
    try:
        #The client method. We don't override native methods, but instead call them from our own wrappers
        def __init__(self, wrapper):
            ## Set up with a wrapper inside
            EClient.__init__(self, wrapper)
    except Exception as ex:
        Log.WriteLog("ibpython.Client",ex)

class Ibpython(Wrapper, Client):    
    def __init__(self, ipaddress, portid, clientid):
        try:
            Wrapper.__init__(self)
            Client.__init__(self, wrapper=self)
    
            self.connect(ipaddress, portid, clientid)
    
            thread = Thread(target = self.run)
            thread.start()
    
            setattr(self, "_thread", thread)
        except Exception as ex:
            Log.WriteLog("ibpython.Ibpython",ex)

    #custom functions
    def read_tickers_csv_file():
        try:
            with open('tickers_basket.csv','r') as f_reader:
                csv_reader = reader(f_reader)
                #iterator
                next(csv_reader)
                count = 0
                for row in csv_reader:
                   if row[7] == "A":
                     count = count + 1
                     objTicker = tickers.Tickers() #new object
                     objTicker.tickerId = count
                     objTicker.symbol = row[0]
                     objTicker.secType = row[1]
                     objTicker.currency = row[2]
                     objTicker.expiry = row[3]
                     objTicker.option_type = row[4]
                     objTicker.strike = row[5]
                     objTicker.exchange = row[6]
                     objTicker.status = row[7]
    
                     objTicker.objContract.symbol = objTicker.symbol
                     objTicker.objContract.secType = objTicker.secType
                     objTicker.objContract.currency = objTicker.currency
                     objTicker.objContract.exchange = objTicker.exchange
                     global_variables.GlobalVariables.tickers_dict[objTicker.tickerId] = objTicker
                     ibapi.reqMktData(objTicker.tickerId, objTicker.objContract, "", False, False, None)
    
                     if objTicker.objContract.exchange == "IDEALPRO":
                         ibapi.reqRealTimeBars(objTicker.tickerId, objTicker.objContract, 5, "MIDPOINT", True, None)
                     else:
                         ibapi.reqRealTimeBars(objTicker.tickerId, objTicker.objContract, 5, "TRADES", True, None)
        except Exception as ex:
            Log.WriteLog("ibpython.read_tickers_csv_file",ex)

#if __name__ == '__main__':
ibapi = Ibpython("127.0.0.1", 7498, 1)
        
