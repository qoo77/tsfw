from tsfw.config import CONFIG
import tsfw.baseFunction as bf
import pandas as pd
import logging
logger = logging.getLogger(__name__)

class StockData():

    csvCol = ["Date", "Vol","TotalAmount","OpenPrice","MaxPrice","MinPrice","ClosePrice","PriceChange","NumberOfTransactions"]

    def __init__(self, stockNum, startDate=None, endDate=None):
        self.trainingDateRegion = lambda:0
        self.testingDateRegion = lambda:0
        self.stockNum = stockNum
        self.__loadData(stockNum, startDate, endDate)

    def __loadDataFromFile_TSEC(self, stockNum):

        try:
            logger.debug("Load File: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            logger.debug("Data Type: " + CONFIG.StockData.dataSource)
            data = pd.read_csv(CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv", header=None, na_values=['--', '---'])
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
            data = pd.read_csv(CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv", na_values='--')
        except IOError:
            logger.error("Load File fail: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            raise Exception('Read CSV fail')

        return data

    def __loadData(self, stockNum, startDate, endDate):

        if CONFIG.StockData.dataSource == "TSEC":
            self.data = self.__loadDataFromFile_TSEC(stockNum)
        else:
            self.data = self.__loadDataFromFile(stockNum)

        logger.debug("Organize Stock Data: " + str(stockNum))
        self.data = self.data.sort_index()
        
        self.data = self.data[~self.data.index.duplicated(keep='last')]# drop same index rows
        self.data = self.data.dropna() # drop nan data

        if CONFIG.StockData.organizeAndOverwriteData == True:
            print(CONFIG.StockData.organizeAndOverwriteData)
            logger.debug("Save File: " + CONFIG.Path.dataDir + "/" + str(stockNum) + ".csv")
            logger.debug("Save File:GGGG")
            logger.debug("Save File:GGGG")
            logger.debug("Save File:GGGG")
            self.data.to_csv("data/" + str(stockNum) + ".csv", index_label=False, mode='w') # write back sorted data to csv

        dateMin = self.data.index.min()
        dateMax = self.data.index.max()

        if startDate!=None and startDate>dateMin:
            self.data = self.data.loc[dateMin:]
            dateMin = startDate

        if endDate!=None and endDate<dateMax:
            self.data = self.data.loc[:dateMax]
            dateMax = endDate

        self.trainingDateRegion.min = dateMin
        self.trainingDateRegion.max = dateMax

        self.testingDateRegion.min = dateMin
        self.testingDateRegion.max = dateMax

        self.trainingData = self.data
        self.testingData = self.data


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

        logger.debug("Training Data Date: " + str(self.trainingDateRegion.min) + " ~ " + str(self.trainingDateRegion.max))
        logger.debug("Testing Data Date: " + str(self.testingDateRegion.min) + " ~ " + str(self.testingDateRegion.max))


    # basic
    def getVol(self, date):
        return self.data["Vol"][date]

    def getTotalAmount(self, date):
        return self.data["TotalAmount"][date]

    def getOpenPrice(self, date):
        return self.data["OpenPrice"][date]

    def getMaxPrice(self, date):
        return self.data["MaxPrice"][date]

    def getMinPrice(self, date):
        return self.data["MinPrice"][date]

    def getClosePrice(self, date):
        return self.data["ClosePrice"][date]

    def getPriceChange(self, date):
        return self.data["PriceChange"][date]

    def getNumberOfTransactions(self, date):
        return self.data["NumberOfTransactions"][date]



