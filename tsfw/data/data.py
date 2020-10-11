import logging
logger = logging.getLogger(__name__)

import importlib
import pandas as pd
from .. import const

class Data(object):
    def __init__(self):
        logger.info("Init data")
        self.parser = None
        # todo
    def setDataSource(self, fileName):
        self.__importDataParser(fileName)
        self.__asignDataProxy()

    def __importDataParser(self, fileName):
        try:
            logger.info("Load data parser: " + fileName)
            self.dataParser = importlib.import_module("tsfw.data." + fileName)
            self.dataProxy = self.dataParser.StockData()
        except:
            logger.error("Load data parser fail: " + fileName)
            raise Exception('No data: ' + fileName)

    def __asignDataProxy(self):
        
        self.loadStockPrice = self.dataProxy.loadStockData
        self.getPrice = self.dataProxy.getPrice


if __name__ == '__main__':
    data = Data()