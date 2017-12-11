import configparser
from tsfw.portfolios import Portfolios as Portfolios
from tsfw.plot import Plot as Plot
from tsfw.stockData import StockData as StockData
from tsfw.recorder import Recorder as Recorder
from tsfw.statistics import Statistics as Statistics
from tsfw.baseFunction import BaseFunction as BaseFunction
import importlib
from datetime import datetime, date, timedelta
import os


class Tsfw():

    def __init__(self):
        print("SimulationFrameWork")
        self.baseFunction = BaseFunction()
        self.stockData = {}
        self.config = self.__loadConfig()
        self.myBudget = self.__loadMyBudget()
        self.statistics = Statistics()
        self.portfolios = Portfolios(self.config.TradingPara, self.myBudget)
        self.recorder = Recorder(self.portfolios, self.stockData, self.myBudget)
        self.algorithm = None
        self.plot = Plot(self.stockData, self.recorder, self.portfolios)
        self.outputPath = self.__initPath()

    def __loadConfig(self):
        print("loadConfig")
        configPath = "tsfw/config.ini"
        config = configparser.ConfigParser()
        config.read(configPath)

        try:
            configuration = lambda:0
            configuration.Path = lambda:0
            configuration.Path.dataDir = config.get("Path", "data dir")
            configuration.Path.outputDir = config.get("Path", "output dir")

            configuration.Budget = lambda:0
            configuration.Budget.money = int(config.get("Budget", "money"))

            configuration.Algorithm = lambda:0

            configuration.TradingPara = lambda:0
            configuration.TradingPara.fees = float(config.get("Trading Para", "fees"))
            configuration.TradingPara.minFees = float(config.get("Trading Para", "min fees"))
            configuration.TradingPara.tax = float(config.get("Trading Para", "tax"))#only at sell
            configuration.TradingPara.canBearish = int(config.get("Trading Para", "can bearish"))
            configuration.TradingPara.tradeUnit = int(config.get("Trading Para", "trade unit"))
        except:
            raise Exception('Wrong Config At ' + configPath)

        return configuration

    def loadAlgorithm(self, name):
        print("loadAlgorithm")
        #name = self.config.Algorithm.name
        try:
            Algorithm = importlib.import_module("tsfw.algorithm." + name)
        except:
            raise Exception('No Algorithm: ' + name)

        self.algorithm = Algorithm.Algorithm(self)

    def __loadMyBudget(self):
        print("loadMyBudget")
        myBudget = lambda:0
        myBudget.initMoney = self.config.Budget.money
        myBudget.remainMoney = myBudget.initMoney
        return myBudget

    def loadStockData(self, stockNum, readAll=False):
        print("loadStockData")

        if readAll==True:
            stockNums = os.listdir(self.config.Path.dataDir)
            stockNums = [x[:-4] for x in stockNums if (x[-4:]==".csv" and (".DS_Store" not in x))]
        else:
            stockNums = [stockNum]


        for stockNum in stockNums:
            if stockNum not in self.stockData:
                stockData = StockData(stockNum, self.config.Path.dataDir)

                self.algorithm.splitData(stockData)

                # init recorder
                if stockNum not in self.recorder.data:
                    self.recorder.addStock(stockNum)

                self.stockData[stockNum] = stockData

        self.portfolios.addStock(stockNum)

    def delStockData(self, stockNum, delAll=False):
        print("delStockData")

        if delAll==True:
            self.stockData = []
        else:
            if stockNum in self.stockData:
                del self.stockData[stockNum]

    def training(self):
        #++
        print("training")
        self.algorithm.train()

    def testing(self):
        print("testing")

        dateList = self.__genDateList(True)

        # prework by stock, load/make statistic here
        for stockNum in self.stockData:
            self.algorithm.test_prework_stock(stockNum)

        # prework, load/make global statistic here
        self.algorithm.test_prework()

        # make decision by day here
        for today in dateList:
            yesterday = self.__getYesterday(today)
            for stockNum in self.stockData:
                if today in self.stockData[stockNum].testingData.index.tolist():
                    
                    if yesterday in self.stockData[stockNum].testingData.index.tolist():
                        self.algorithm.test_strategy(stockNum, today, yesterday)
                    self.recorder.updatePerformance(stockNum, today)

            # make today's all stock summary for tomorrow's decision
            self.algorithm.test_dateSummary(today)

        # after work by stock
        for stockNum in self.stockData:
            self.algorithm.test_afterwork_stock(stockNum)

        # after work
        self.algorithm.test_afterwork()

    def saveResult(self):
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        self.portfolios.saveResult(self.outputPath)
        self.recorder.saveResult(self.outputPath)
        self.plot.saveResult(self.outputPath)

    def __initPath(self):
        dirName = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        outputPath = self.config.Path.outputDir + "/" + dirName

        return outputPath

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

    def __getYesterday(self, today):
        today = datetime.strptime(today, "%Y-%m-%d")
        yesterday = today - timedelta(1)
        yesterday = yesterday.strftime("%Y-%m-%d")

        return yesterday

    def reset(self):
        dic = vars(self)
        for i in dic.keys():
            dic[i] = None

        self.__init__()
        