import pandas as pd
from numpy import isnan
import logging
logger = logging.getLogger(__name__)

class BaseFunction():
    """docstring for test"""
    def __init__(self):
        pass

    def isIntersect(self, date, line1, line1Col, line2, line2Col, line1Low2High, continuedDate=1):

        # line1 dataframe -> serise
        if type(line1)==pd.core.series.Series:
            pass
        elif type(line1)==pd.core.frame.DataFrame:
            line1 = line1[line1Col]
        else:
            raise Exception("line1 type error: " + type(line1))

        line1Loc = line1.index.tolist().index(date)

        # line1 left boundary
        if (line1Loc-continuedDate)<0:
            return False

        line1List = line1.iloc[(line1Loc-continuedDate):(line1Loc+1)].tolist()

        # line1 nan
        if isnan(line1List).any():
            return False

        # line2 dataframe -> serise
        if type(line2)==pd.core.series.Series:
            pass
        elif type(line2)==pd.core.frame.DataFrame:
            line2 = line2[line2Col]
        else:
            raise Exception("line2 type error: " + type(line2))

        line2Loc = line2.index.tolist().index(date)

        # line2 left boundary
        if (line2Loc-continuedDate)<0:
            return False

        line2List = line2.iloc[(line2Loc-continuedDate):(line2Loc+1)].tolist()

        # line2 nan
        if isnan(line2List).any():
            return False

        # compare idx 0, idx rest
        if line1Low2High==True:
            if line1List[0]>=line2List[0]:
                return False
            elif all(line1List[x+1]<=line2List[x+1] for x in range(continuedDate)):
                return False
        else:
            if line1List[0]<=line2List[0]:
                return False
            elif all(line1List[x+1]>=line2List[x+1] for x in range(continuedDate)):
                return False

        return True


