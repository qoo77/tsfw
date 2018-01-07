import tsfw.config as config
config.init()
CONFIG = config.CONFIG

from tsfw.portfolios import Portfolios as Portfolios
from tsfw.plot import Plot as Plot
from tsfw.stockData import StockData as StockData
from tsfw.recorder import Recorder as Recorder
from tsfw.statistics import Statistics as Statistics
import tsfw.baseFunction as bf
import importlib
from datetime import datetime, date, timedelta
import os
from shutil import rmtree

import logging
logger = logging.getLogger(__name__)



class Tsfw():

    def __init__(self):
        self.outputPath = self.__initPath()
        self.logger = self.__initLogging()

        logger.info("Init Tsfw")

        self.stockData = {}
        self.myBudget = self.__loadMyBudget()
        self.statistics = Statistics()
        self.portfolios = Portfolios(self.stockData, self.myBudget)
        self.recorder = Recorder(self.portfolios, self.stockData, self.myBudget)
        self.algorithm = None
        self.plot = Plot(self.stockData, self.recorder, self.portfolios)


    def __initPath(self):
        if CONFIG.Debug.debug:
            dirName = "debug"
            outputPath = CONFIG.Path.outputDir + "/" + dirName
            if os.path.exists(outputPath):
                rmtree(outputPath)             
        else:
            dirName = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
            outputPath = CONFIG.Path.outputDir + "/" + dirName

        return outputPath

    def __initLogging(self):
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        path = self.outputPath + "/" + "tsfw.log"

        logging.TRADE = 15
        logging.addLevelName(logging.TRADE, "TRADE")

        logLvMapping = [logging.DEBUG, 
                            logging.TRADE, 
                            logging.INFO, 
                            logging.WARNING, 
                            logging.ERROR, 
                            logging.CRITICAL]

        logFileLv = logLvMapping[CONFIG.LogLevel.logFile]
        commandLineLv = logLvMapping[CONFIG.LogLevel.commandLine]


        logging.basicConfig(level=logFileLv,
            format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S',
            filename=path)
        
        console = logging.StreamHandler()
        console.setLevel(commandLineLv)

        formatter = logging.Formatter('%(name)-20s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)


    def __loadMyBudget(self):
        myBudget = lambda:0
        myBudget.initMoney = CONFIG.Budget.money
        myBudget.remainMoney = myBudget.initMoney
        return myBudget

    def loadAlgorithm(self, name):
        try:
            logger.info("Load Algorithm: " + name)
            Algorithm = importlib.import_module("tsfw.algorithm." + name)
        except:
            logger.error("Load Algorithm: " + name + " fail")
            raise Exception('No Algorithm: ' + name)

        self.algorithm = Algorithm.Algorithm(self)


    def loadStockData(self, stockNum, startDate=None, endDate=None, readAll=False):
        
        if self.algorithm==None:
            logger.warning("No algorithm loaded")
            return

        if readAll==True:
            logger.info("Load All Stock Data")
            stockNums = os.listdir(CONFIG.Path.dataDir)
            stockNums = [x[:-4] for x in stockNums if (x[-4:]==".csv" and (".DS_Store" not in x))]         
        else:
            stockNums = [stockNum]
            
        for stockNum in stockNums:
            if stockNum not in self.stockData:
                logger.info("Load Stock Data: " + str(stockNum) + ", data range= " + str(startDate) + " ~ " + str(endDate))
                stockData = StockData(stockNum, startDate, endDate)

                self.algorithm.splitData(stockData)

                # init recorder
                if stockNum not in self.recorder.data:
                    self.recorder.addStock(stockNum)

                self.stockData[stockNum] = stockData

        self.portfolios.addStock(stockNum)


    def delStockData(self, stockNum, delAll=False):
        
        if delAll==True:
            self.stockData = []
            logger.info("Delete All Stock Data")
        else:
            if stockNum in self.stockData:
                logger.info("Delete Stock Data: " + str(stockNum))
                del self.stockData[stockNum]
            else:
                logger.warning("No " + str(stockNum) + " Stock Data")            


    def training(self):
        logger.info("Training start")
        if self.algorithm == None:
            logger.log(logging.WARNING, "No algorithm loaded")
            return

        if len(self.stockData) == 0:
            logger.log(logging.WARNING, "No stock input")
            return
        
        self.algorithm.train()
        logger.info("Training end")


    def testing(self):
        logger.info("Testing start")

        if self.algorithm == None:
            logger.log(logging.WARNING, "No algorithm loaded")
            return

        if len(self.stockData) == 0:
            logger.log(logging.WARNING, "No stock input")
            return

        dateList = self.__genDateList(True)

        # prework by stock, load/make statistic here
        for stockNum in self.stockData:
            self.algorithm.test_prework_stock(stockNum)

        # prework, load/make global statistic here
        self.algorithm.test_prework()

        # make decision by day here
        for today in dateList:
            logger.debug(today)
            yesterday = bf.getYesterday(today)
            for stockNum in self.stockData:
                if today in self.stockData[stockNum].testingData.index.tolist():               
                    if yesterday in self.stockData[stockNum].testingData.index.tolist():
                        self.algorithm.test_strategy(stockNum, today, yesterday)
                    self.recorder.updatePerformance(stockNum, today)

                    # last record in the testing data of this stock, do check out or some statistic 
                    if today==self.stockData[stockNum].testingDateRegion.max:
                        self.algorithm.test_afterwork_stock(stockNum, today)

            # make today's all stock summary for tomorrow's decision
            self.algorithm.test_dateSummary(today)


        # after work
        self.algorithm.test_afterwork()

        logger.info("Testing end")


    def saveResult(self):
        logger.info("Save Result")
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        self.portfolios.saveResult(self.outputPath)
        self.recorder.saveResult(self.outputPath)
        self.plot.saveResult(self.outputPath)


    def __genDateList(self, isTestData):
        minList = []
        maxList = []
        for stockNum in self.stockData:

            if isTestData==True:
                minList.append(self.stockData[stockNum].testingDateRegion.min)
                maxList.append(self.stockData[stockNum].testingDateRegion.max)
            else:
                minList.append(self.stockData[stockNum].trainingDateRegion.min)
                maxList.append(self.stockData[stockNum].trainingDateRegion.max)

        startDate = datetime.strptime(min(minList), "%Y-%m-%d")
        endDate = datetime.strptime(max(maxList), "%Y-%m-%d")
        deltaDate = (endDate-startDate).days + 1

        dateList  = [(startDate+timedelta(x)).strftime("%Y-%m-%d") for x in range(int(deltaDate))]

        return dateList
    

    def reset(self):
        logger.warning("Reset tsfw module")
        dic = vars(self)
        for key in dic.keys():
            dic[key] = None

        self.__init__()
        