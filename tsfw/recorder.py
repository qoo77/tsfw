from tsfw.config import CONFIG
import tsfw.baseFunction as bf
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

class Recorder():
    recorderIndex = ["Market Value",
                        "Today Volume",
                        "Total Volume"]


    def __init__(self, portfolios, stockData, myBudget):
        self.data = {}
        self.portfolios = portfolios
        self.stockData = stockData
        self.myBudget = myBudget

    def addStock(self, stockNum):
        self.data[stockNum] = pd.DataFrame(columns = self.recorderIndex)

    def updatePerformance(self, stockNum, date):

        if stockNum in self.portfolios.data:
            marketValue = self.__calcMarketValue(stockNum, date)
            todayVolume = self.__calcTodayVolume(stockNum, date)
            totalVolume = self.__calcTotalVolume(stockNum, date)

            if todayVolume!=0:
                logger.debug(stockNum + ": Market Val=" + str(marketValue) + ", Today Vol=" + str(todayVolume) + ", Total Vol=" + str(totalVolume))
        else:
            marketValue = 0
            todayVolume = 0
            totalVolume = 0
        marketValue += self.myBudget.remainMoney


        self.data[stockNum].loc[date] = [marketValue,
                                        int(todayVolume),
                                        int(totalVolume)]


    def __calcMarketValue(self, stockNum, date):
        return self.portfolios.data[stockNum].tradeSummary["Volume"] * self.stockData[stockNum].getClosePrice(date)

    def __calcTodayVolume(self, stockNum, date):
        for intent in self.portfolios.tradeType:
            if date in self.portfolios.data[stockNum].tradeHistory[intent].index.tolist():
                return self.portfolios.data[stockNum].tradeHistory[intent].loc[date]["Volume"]

        return 0

    def __calcTotalVolume(self, stockNum, date):
        return self.portfolios.data[stockNum].tradeSummary["Volume"]


    def saveResult(self, path):
        for stockNum in self.data:
            filePath = path + "/" + stockNum

            if not os.path.exists(filePath):
                os.makedirs(filePath)

            logger.debug("Save File:" + filePath + "/recorder.csv")
            self.data[stockNum].to_csv(filePath + "/recorder.csv", sep='\t', float_format='%.2f', index_label=False, mode='w')
