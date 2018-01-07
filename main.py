import sys
from tsfw.tsfw import Tsfw as Tsfw


def main():     

    tsfw = Tsfw()
    tsfw.loadAlgorithm("BBANDS")

    #tsfw.loadStockData(None, readAll=True)
    #tsfw.loadStockData("2414")
    tsfw.loadStockData("2414", startDate="2001-03-01", endDate="2001-07-02")

    tsfw.training()
    tsfw.testing()
    tsfw.saveResult()
    #tsfw.reset()


if __name__ == '__main__':
    sys.exit(main())