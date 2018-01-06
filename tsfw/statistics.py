from tsfw.config import CONFIG
import tsfw.baseFunction as bf
import pandas as pd
import talib
import logging
logger = logging.getLogger(__name__)

class Statistics():

    def __init__(self):
        self.data = {}

    def load_Talib_BBANDS(self, stockNum, stockData, timeperiod=5, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA):
        if not self.chkTAExist(stockNum, "bbands"):
            logger.info(str(stockNum) + ": Load Talib BBANDS, timeperiod=" + str(timeperiod) + ", nbdevup=" + str(nbdevup) + ", nbdevdn=" + str(nbdevdn) + ", matype=" + str(matype))
            df = pd.DataFrame(stockData["ClosePrice"])
            df.rename(columns={'ClosePrice': 'close'}, inplace=True)

            # upperband, middleband, lowerband
            self.data[stockNum]["bbands"] = talib.abstract.Function("bbands")(df, timeperiod, nbdevup, nbdevdn, matype)

            # %b (pb), def:(close-lower)/(upper-lower) 
            self.data[stockNum]["bbands"]["pb"] = (stockData["ClosePrice"] - self.data[stockNum]["bbands"]["lowerband"])/(self.data[stockNum]["bbands"]["upperband"] - self.data[stockNum]["bbands"]["lowerband"])

            # BW, def:(upper-lower)/middle
            self.data[stockNum]["bbands"]["bw"] = (self.data[stockNum]["bbands"]["upperband"] - self.data[stockNum]["bbands"]["lowerband"])/self.data[stockNum]["bbands"]["middleband"]

    def load_Talib_MACD(self, stockNum, stockData, fastperiod=12, slowperiod=26, signalperiod=9):
        if not self.chkTAExist(stockNum, "macd"):
            logger.info(str(stockNum) + ": Load Talib MACD, fastperiod=" + str(fastperiod) + ", slowperiod=" + str(slowperiod) + ", signalperiod=" + str(signalperiod))
            df = pd.DataFrame(stockData["ClosePrice"])
            df.rename(columns={'ClosePrice': 'close'}, inplace=True)

            # macd, macd signal, macd hist
            self.data[stockNum]["macd"] = talib.abstract.Function("macd")(df, fastperiod, slowperiod, signalperiod)

    def chkTAExist(self, stockNum, TAName):

        if stockNum not in self.data:
            self.data[stockNum] = {}

        if TAName not in self.data[stockNum]:
            return False
        else:
            logger.warning(str(stockNum) + ": Talib " + TAName + " already exist") 
            return True
