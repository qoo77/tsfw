import logging
logger = logging.getLogger(__name__)

from ..tsfw import gConfig
from .. import const

class Stock():
    def __init__(self, stock, amount):
        logger.info("Init " + self.__class__.__name__)
        self.name = stock
        self.amount = amount

    def upcateStock(self, amount):
        self.amount = self.amount + amount

if __name__ == '__main__':
    stock = Stock("test", 0)