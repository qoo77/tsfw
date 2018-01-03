import sys
from tsfw.tsfw import Tsfw as Tsfw


def main():     

    tsfw = Tsfw()
    tsfw.parseStockData("7777")
    tsfw.loadAlgorithm("BBANDS")
    #tsfw.loadAlgorithm("test")
    #tsfw.loadStockData("1111")
    #tsfw.loadStockData("2002")
    #tsfw.loadStockData("7773939889")
    #tsfw.loadStockData("1111", readAll=True)
    tsfw.loadStockData("1101", startDate="2011-09-06", endDate="2011-09-20")
    #tsfw.loadStockData("1102")
    #tsfw.delStockData("1102")

    tsfw.training()
    tsfw.testing()
    tsfw.saveResult()
    #tsfw.reset()


if __name__ == '__main__':
    sys.exit(main())