import logging
logger = logging.getLogger(__name__)

from ..tsfw import gConfig
from .. import const

class Cash():
    def __init__(self, amount, currency):
        logger.info("Init " + self.__class__.__name__)
        self.amount = amount
        self.currency = currency

    def upcateCash(self, amount):
        self.amount = self.amount + amount

if __name__ == '__main__':
    cash = Cash(100000, "USD")