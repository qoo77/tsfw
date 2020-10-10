import logging
logger = logging.getLogger(__name__)

from .baseRecorder import BaseRecorder
from .. import const
import pandas as pd

class TradeRecorder(BaseRecorder):
    def __init__(self):
        logger.info("Init " + self.__class__.__name__)
        self.stock = dict()
        self.recorderColumns = ["tradeType", "amount", "price"]

    def initStock(self, stock):
        logger.debug("Init stock " + stock + self.__class__.__name__)
        self.stock[stock] = pd.DataFrame(columns = self.recorderColumns)

if __name__ == '__main__':
    tradeRecorder = TradeRecorder()