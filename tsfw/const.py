from enum import Enum

class CustomEnum(Enum):
    def __repr__(self):
        return "%s.%s" % (
            self.__class__.__name__, self._name_)
    
    def __str__(self):
         return self.name

class TRADE(CustomEnum):
    BUY = 0
    SELL = 1
    BUYTOCOVER = 2 
    SELLSHORT = 3

class PRICE(CustomEnum):
    OPEN = 0
    HIGH = 1
    LOW = 2
    CLOSE = 3
    ADJCLOSE = 4
    VOLUME = 5