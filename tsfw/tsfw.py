from . import configParser
gConfig = configParser.init("config.ini")

import os
import sys
import logging

from .algorithm import algorithm
from .data import data
from .positions import positions
from .recorder import tradeRecorder
from .recorder import performanceRecorder

logger = logging.getLogger(__name__)

class Tsfw():
    def __init__(self, tittle = None, configName = "config.ini"):
        logger.info("Init Tsfw")
        self.__initFramework(tittle, configName)
        self.algorithm = None  
        self.data = data.Data()
        self.positions = positions.Positions()
        self.performanceRecorder = performanceRecorder.PerformanceRecorder()
        self.tradeRecorder = tradeRecorder.TradeRecorder() 

    def __initFramework(self, tittle, configName):
        self.__initLog()
        self.__initTestDescription(tittle)

    def __initTestDescription(self, tittle):
        if tittle is None:
            tittle = "test"
        self.tittle = tittle
        logger.info("TSFW project name: %s", tittle)

    def __initLog(self):
        # todo: implement save log file later

        # Add trade category in logging
        logging.TRADE = 15
        logging.addLevelName(logging.TRADE, "TRADE")

        logLevel = [logging.DEBUG, logging.TRADE, logging.INFO, 
                    logging.WARNING, logging.ERROR, logging.CRITICAL]

        cmdLineLogLv = logLevel[int(gConfig.LogLevel.commandline)]

        logging.basicConfig(stream=sys.stdout, 
                            level=cmdLineLogLv,
                            format='%(name)-30s: %(levelname)-8s %(message)s')

    def setDataSource(self, fileName):
        self.data.setDataSource(fileName)

    def setAlgorithm(self, name):
        if self.algorithm is None:
            self.algorithm = algorithm.Algorithm(name)
        else:
            # todo: switch algorithm
            raise NotImplementedError("Switch algorithm not implement")

    def loadStockData(self, inputStock, startDate=None, endDate=None, readAll=False):

        logger.info("Start load stock")

        if readAll==True:
            logger.info("Load all stock")
            # todo: adjust how to load all
            raise NotImplementedError("Load all not implement")
        elif type(inputStock) is list:
            logger.info("Load stock list: " + str(inputStock))
            stocks = inputStock
        elif type(inputStock) is str:
            logger.info("Load single stock: " + inputStock)
            stocks = [inputStock]
        else:
            raise Exception("inputStock type = " + type(inputStock))
            
        # Load stock data from data proxy
        for stock in stocks:
            logger.info("Load stock: " + stock)
            # load stock data from data
            self.data.loadStockPrice(stock, startDate, endDate)
            # init trade history in tradeRecords
            self.tradeRecorder.initStock(stock)
            # init performance history performanceRecords
            self.performanceRecorder.initStock(stock)
            

    def delStockData(self, stockNum, delAll=False):
        # todo
        raise NotImplementedError("Not implement")      


    def training(self):
        logger.info("Training start")
        # todo
        logger.info("Training end")


    def testing(self):
        logger.info("Testing start")
        # todo
        logger.info("Testing end")


    def saveResult(self):
        logger.info("Save Result")
        # todo

    def reset(self):
        logger.warning("Reset tsfw module")
        dic = vars(self)
        for key in dic.keys():
            dic[key] = None

        self.__init__()

if __name__ == '__main__':
    tsfw = Tsfw()