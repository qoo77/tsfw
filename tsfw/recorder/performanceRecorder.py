import logging
logger = logging.getLogger(__name__)

from .baseRecorder import BaseRecorder
from .. import const
import pandas as pd

class PerformanceRecorder(BaseRecorder):
    def __init__(self):
        logger.info("Init " + self.__class__.__name__)
        self.stock = dict()
        self.recorderColumns = ["earn", "compareSpy"]

    def initStock(self, stock):
        logger.debug("Init stock " + stock + self.__class__.__name__)
        self.stock[stock] = pd.DataFrame(columns = self.recorderColumns)

if __name__ == '__main__':
    performanceRecorder = PerformanceRecorder()