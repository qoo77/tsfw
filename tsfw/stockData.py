import pandas as pd
import logging
logger = logging.getLogger(__name__)

class StockData():
    def __init__(self, stockNum, path):
        self.trainingDateRegion = lambda:0
        self.testingDateRegion = lambda:0
        self.stockNum = stockNum
        self.path = path
        self.__loadDataFromFile(stockNum)

    def __loadDataFromFile(self, stockNum):

        startDate = None
        endDate = None

        try:
            logger.debug("Load File: " + self.path + "/" + str(stockNum) + ".csv")
            self.data = pd.read_csv(self.path + "/" + str(stockNum) + ".csv", na_values='--')
        except IOError:
            logger.error("Load File fail: " + self.path + "/" + str(stockNum) + ".csv")
            raise Exception('Read CSV fail')

        logger.debug("Organize Stock Data: " + str(stockNum))
        self.data = self.data.sort_index()
        
        self.data = self.data[~self.data.index.duplicated(keep='last')]# drop same index rows
        self.data = self.data.dropna() # drop nan data

        logger.debug("Save File: " + self.path + "/" + str(stockNum) + ".csv")
        self.data.to_csv("data/" + str(stockNum) + ".csv", index_label=False, mode='w') # write back sorted data to csv

        self.trainingDateRegion.min = self.data.index.min()
        self.trainingDateRegion.max = self.data.index.max()

        self.testingDateRegion.min = self.data.index.min()
        self.testingDateRegion.max = self.data.index.max()

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



