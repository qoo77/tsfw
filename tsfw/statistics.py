import pandas as pd
import talib
#import os

class Statistics():

    def __init__(self):
        self.data = {}
        self.talib = talib
        self.taFunc = talib.abstract.Function
        self.MA_Type = talib.MA_Type


    def chkTAExist(self, stockNum, TAName):

        if stockNum not in self.data:
            self.data[stockNum] = {}
            return False

        if TAName not in self.data[stockNum]:
            return False
        else:
            return True