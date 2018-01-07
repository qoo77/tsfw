from tsfw.config import CONFIG
from tsfw.const import*
import tsfw.baseFunction as bf
import pandas as pd
import logging
logger = logging.getLogger(__name__)

class StockData():

    csvCol = ["Date", "Vol", "TotalAmount", "OpenPrice", "MaxPrice", "MinPrice", "ClosePrice", "PriceChange", "NumberOfTransactions"]

    def __init__(self, stockNum, startDate=None, endDate=None):
        self.trainingDateRegion = lambda:0
        self.testingDateRegion = lambda:0
        self.stockNum = stockNum
        self.__loadData(stockNum, startDate, endDate)

    def __loadDataFromFile_TSEC(self, stockNum):

        try:
            logger.debug("Load File: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            logger.debug("Data Type: " + CONFIG.StockData.dataSource)
            data = pd.read_csv(CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv", header=None, na_values=['--', '---', 'X0.00', 'X'])
        except IOError:
            logger.error("Load File fail: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            raise Exception('Read CSV fail')

        data.columns = self.csvCol

        dateList = data["Date"].tolist()

        dateList = bf.twDate2WestDate(dateList, formatChk=1)
        data["Date"] = dateList

        #data.Date = pd.to_datetime(data.Date)
        data.set_index("Date", inplace=True)

        return data

    def __loadDataFromFile(self, stockNum):
        try:
            logger.debug("Load File: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            logger.debug("Data Type: default")
            data = pd.read_csv(CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv", na_values='--')
        except IOError:
            logger.error("Load File fail: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            raise Exception('Read CSV fail')

        return data

    def __loadData(self, stockNum, inputStartDate, inputEndDate):

        if CONFIG.StockData.dataSource == "TSEC":
            self.data = self.__loadDataFromFile_TSEC(stockNum)
        else:
            self.data = self.__loadDataFromFile(stockNum)

        logger.debug("Organize Stock Data: " + str(stockNum))
        self.data = self.data.sort_index()
        
        self.data = self.data[~self.data.index.duplicated(keep='last')]# drop same index rows
        self.data = self.data.dropna() # drop nan data

        # Organize stock data and save back to original csv file
        if CONFIG.StockData.organizeAndOverwriteData == True:
            print(CONFIG.StockData.organizeAndOverwriteData)
            logger.debug("Save File: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            self.data.to_csv("data/" + str(stockNum) + ".csv", index_label=False, mode='w') # write back sorted data to csv

        dateMin = self.data.index.min()
        dateMax = self.data.index.max()

        if inputStartDate!=None and inputStartDate<dateMin:
            logger.warning("Input start date out of range, file start date=" + dateMin + ", input start date=" + inputStartDate)
            self.data = self.data.loc[dateMin:]
        elif inputStartDate!=None:
            self.data = self.data.loc[inputStartDate:]
            dateMin = inputStartDate

        if inputEndDate!=None and inputEndDate>dateMax:
            logger.warning("Input end date out of range, file end date=" + dateMax + ", input end date=" + inputEndDate)
            self.data = self.data.loc[:dateMax]
        elif inputStartDate!=None:
            self.data = self.data.loc[:inputEndDate]
            dateMax = inputEndDate

        self.trainingDateRegion.min = dateMin
        self.trainingDateRegion.max = dateMax

        self.testingDateRegion.min = dateMin
        self.testingDateRegion.max = dateMax

        self.trainingData = self.data
        self.testingData = self.data

    def chkCanTrade(self, intent, date):

        if CONFIG.TradingPara.market == "TW":
            # check 7% or 10% by date ++
            # TW stock max increase/decrease  7% before 2015/6/1
            # TW stock max increase/decrease 10% after  2015/6/1
            if date<"2015-06-01":
                maxIncDecPercent = 0.07
            else:
                maxIncDecPercent = 0.1

            # ignore TW complex formula, use 7% or 10% x 0.95
            maxIncDecPercent = maxIncDecPercent*0.95

            try:
                todayIncDecPercent = self.getPriceChange(date)/self.getClosePrice(date, previousDay=1)
            except:
                # divide by zero or boundary case
                logger.debug("chkCanTrade() value error, " + str(date) + ", " + str(self.getPriceChange(date)) + ", " + str(self.getClosePrice(date, previousDay=1)))
                todayIncDecPercent = 0

            if intent=="buy":
                if todayIncDecPercent >= maxIncDecPercent:
                    ret = TRADE_REACH_MAX_INCREASE_BUY
                else:
                    ret = TRADE_ALLOWED
            elif intent=="bearishBuy":
                #++
                if CONFIG.TradingPara.canBearish:
                    if todayIncDecPercent >= maxIncDecPercent:
                        ret = TRADE_REACH_MAX_INCREASE_BEARISHBUY
                    else:
                        ret = TRADE_ALLOWED
                else:
                    ret = TRADE_NO_BEARISHBUY
            elif intent=="sell":
                if -todayIncDecPercent >= maxIncDecPercent:
                    ret = TRADE_REACH_MAX_INCREASE_SELL
                else:
                    ret = TRADE_ALLOWED
            elif intent=="bearishSell":
                #++
                if CONFIG.TradingPara.canBearish:
                    if -todayIncDecPercent >= maxIncDecPercent:
                        ret = TRADE_REACH_MAX_INCREASE_BEARISHSELL
                    else:
                        ret = TRADE_ALLOWED
                else:
                    ret = TRADE_NO_BEARISHSELL
        else:
            if intent=="buy":
                #++
                ret = TRADE_ALLOWED
            elif intent=="bearishBuy":
                #++
                if CONFIG.TradingPara.canBearish:
                    ret = TRADE_ALLOWED
                else:
                    ret = TRADE_NO_BEARISHBUY
            elif intent=="sell":
                #++
                ret = TRADE_ALLOWED
            elif intent=="bearishSell":
                #++
                if CONFIG.TradingPara.canBearish:
                    ret = TRADE_ALLOWED
                else:
                    ret = TRADE_NO_BEARISHSELL

        if ret==TRADE_ALLOWED:
            # for speed up
            return ret
        elif ret==TRADE_REACH_MAX_INCREASE_BUY:
            logger.log(logging.TRADE, "Reach max increase, cant buy")
        elif ret==TRADE_REACH_MAX_DECREASE_BUY:
            logger.log(logging.TRADE, "Reach max decrease, cant buy")
        elif ret==TRADE_REACH_MAX_INCREASE_BEARISHBUY:
            logger.log(logging.TRADE, "Reach max increase, cant bearishBuy")
        elif ret==TRADE_REACH_MAX_DECREASE_BEARISHBUY:
            logger.log(logging.TRADE, "Reach max decrease, cant bearishBuy")
        elif ret==TRADE_NO_BEARISHBUY:
            logger.log(logging.TRADE, "No bearish by config, cant bearishBuy")
        elif ret==TRADE_REACH_MAX_INCREASE_SELL:
            logger.log(logging.TRADE, "Reach max increase, cant sell")
        elif ret==TRADE_REACH_MAX_DECREASE_SELl:
            logger.log(logging.TRADE, "Reach max decrease, cant sell")
        elif ret==TRADE_REACH_MAX_INCREASE_BEARISHSELL:
            logger.log(logging.TRADE, "Reach max increase, cant bearishSell")
        elif ret==TRADE_REACH_MAX_DECREASE_BEARISHSELL:
            logger.log(logging.TRADE, "Reach max decrease, cant bearishSell")
        elif ret==TRADE_NO_BEARISHSELL:
            logger.log(logging.TRADE, "No bearish by config, cant bearishSell")
        

        return ret


    def splitData(self, cutDate, type=""):
        logger.info("Split data, type=" + type)

        if type == "AllTrain":
            self.testingDateRegion.min = None
            self.testingDateRegion.max = None
            self.testingData = None
        elif type == "AllTest":
            self.trainingDateRegion.min = None
            self.trainingDateRegion.max = None
            self.trainingData = None
        else:
            self.trainingData=loc[:cutDate]
            self.trainingDateRegion.max=cutDate

            self.testingData=loc[cutDate:]
            self.testingData.drop(self.testingData.index[0])
            self.testingDateRegion.min=a.index.tolist()[0]

        logger.info("Training Data Date: " + str(self.trainingDateRegion.min) + " ~ " + str(self.trainingDateRegion.max))
        logger.info("Testing Data Date: " + str(self.testingDateRegion.min) + " ~ " + str(self.testingDateRegion.max))


    # basic
    def getVol(self, date, previousDay=0):
        if not previousDay:
            return self.data["Vol"][date]
        else:
            idx = self.data.index.get_loc(date)
            return self.data["Vol"].iloc[idx-previousDay]          

    def getTotalAmount(self, date, previousDay=0):
        return self.data["TotalAmount"][date]

    def getOpenPrice(self, date, previousDay=0):
        return self.data["OpenPrice"][date]

    def getMaxPrice(self, date, previousDay=0):
        return self.data["MaxPrice"][date]

    def getMinPrice(self, date, previousDay=0):
        return self.data["MinPrice"][date]

    def getClosePrice(self, date, previousDay=0):
        if not previousDay:
            return self.data["ClosePrice"][date]
        else:
            idx = self.data.index.get_loc(date)
            return self.data["ClosePrice"].iloc[idx-previousDay]  

    def getPriceChange(self, date, previousDay=0):
        return self.data["PriceChange"][date]

    def getNumberOfTransactions(self, date, previousDay=0):
        return self.data["NumberOfTransactions"][date]



