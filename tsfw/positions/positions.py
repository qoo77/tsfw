import logging
logger = logging.getLogger(__name__)

from ..tsfw import gConfig
from .. import const
from .balance import Balance


class Positions():
    def __init__(self):
        logger.info("Init " + self.__class__.__name__)
        self.initialBalance = Balance()
        self.balance = Balance()

if __name__ == '__main__':
    positions = Positions()