import logging
logger = logging.getLogger(__name__)

from ..tsfw import gConfig
from .. import const
from .cash import Cash
from .stock import Stock

class Balance():
    def __init__(self, cashAmount = gConfig.Positions.initialfund, currency = gConfig.Positions.currency):
        logger.info("Init " + self.__class__.__name__)
        self.cash = Cash(cashAmount, currency)
        self.stock = dict()

        # todo: design interface for initial stock in config.ini
        """
        for stock in gConfig.Positions.xxx:
            createStock(stock, amount)
            pass
        """

    def createStock(self, stock, amount):
        logger.debug("Create stock: " + stock + "amount: " + str(amount))
        if self.isStockExist(stock):
            raise Exception("duplicate stock: " + stock)
        self.stock[stock] = Stock(stock, amount)

    def updateBalance(self, tradeType, stock, amount, price):
        if not self.isStockExist(stock):
            self.createStock(stock, amount)
        
        # SELL and SELLSHORT use negative "amount"
        if tradeType == const.TRADE.SELL or tradeType == const.TRADE.SELLSHORT:
            amount = -amount

        # update cash (logic check should be upper layer)   
        self.cash.updateCash(amount * price)

        # update stock (logic check should be upper layer)
        self.stock[stock].updateStock(amount)

    def isStockExist(self, stock):
        return stock in self.stock

    

if __name__ == '__main__':
    balance = Balance()