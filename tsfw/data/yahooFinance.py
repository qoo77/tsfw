import logging
logger = logging.getLogger(__name__)

import pandas as pd
import yfinance as yf

class StockData(object):
    def __init__(self):
        logger.info("Stock data init")
        self.data = dict()

    def loadStockData(self, stock, dateStart, dateEnd):
        self.data[stock] = yf.download(stock, dateStart, dateEnd)
        return True

    def getPrice(self, stock, date, price):
        return self.data[stock].loc[date, price]

if __name__ == '__main__':
    stockData = StockData()




