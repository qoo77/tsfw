import sys
from tsfw.tsfw import Tsfw


def main():     

    tsfw = Tsfw("test build")
    tsfw.setAlgorithm("algorithm_a")

    tsfw.setDataSource("yahooFinance")
    tsfw.loadStockData(["AAPL", "TSLA"], startDate="2020-06-01", endDate="2020-10-02")

    tsfw.training()
    tsfw.testing()
    tsfw.saveResult()

    #tsfw.reset()


if __name__ == '__main__':
    main()
    