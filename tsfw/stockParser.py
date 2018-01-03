from tsfw.config import CONFIG
import logging
logger = logging.getLogger(__name__)

class StockParser():
    def __init__(self):
        pass
        
    def parseStock(self, stockNum, startDate=None, endDate=None, parseAll=False):
        if parseAll:
            #++ get all stock list
            stockList = []
        else:
            stockList = [stockNum]

        for stockNum in stockList:
            pass
    