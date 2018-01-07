from tsfw.config import CONFIG
from tsfw.const import*
import tsfw.baseFunction as bf
import pandas as pd
import os

import logging
logger = logging.getLogger(__name__)

class Portfolios():
    tradeHistoryCol = ["Intent",
                        "Price",
                        "Volume",
                        "Cash change",
                        "Remarks"]
    tradeType = ["buy",
                    "sell",
                    "bearishBuy",
                    "bearishSell"]

    def __init__(self, stockData, myBudget):
        self.stockData = stockData
        self.data = {}
        self.myBudget = myBudget

    def addStock(self, stockNum):
        if stockNum not in self.data:
            self.data[stockNum] = lambda:0
            self.data[stockNum].tradeHistory = {}
            self.data[stockNum].tradeHistory["buy"] = pd.DataFrame(columns=self.tradeHistoryCol)
            self.data[stockNum].tradeHistory["sell"] = pd.DataFrame(columns=self.tradeHistoryCol)
            self.data[stockNum].tradeHistory["bearishBuy"] = pd.DataFrame(columns=self.tradeHistoryCol)
            self.data[stockNum].tradeHistory["bearishSell"] = pd.DataFrame(columns=self.tradeHistoryCol)
            self.data[stockNum].tradeSummary = pd.Series(0, dtype=float,index=
                ["Total Profit",
                "Total Profit With Fees And Tax",
                "Volume",
                "Average Buy Cost"])


    def __append(self, stockNum, date, intent, price, vol, remarks):
        cashChange = -vol*price - self.__tradingLoss(intent, vol, price)
        averageBuyCost = self.__calcAverageBuyCost(stockNum, price, vol)

        # record history
        (self.data[stockNum].tradeHistory[intent]).loc[date] = [intent,
                                                                price,
                                                                vol,
                                                                cashChange,
                                                                remarks]

        # update tradeSummary
        (self.data[stockNum].tradeSummary)["Total Profit"] += (price*(-vol))
        (self.data[stockNum].tradeSummary)["Total Profit With Fees And Tax"] += cashChange
        (self.data[stockNum].tradeSummary)["Volume"] += vol
        if intent=="buy":# ++consider bearishBuy
            (self.data[stockNum].tradeSummary)["Average Buy Cost"] = averageBuyCost



    def __calcAverageBuyCost(self, stockNum, price, vol):
        pre_price = (self.data[stockNum].tradeSummary)["Average Buy Cost"]
        pre_vol = self.data[stockNum].tradeSummary["Volume"]

        costPrevious = pre_price*pre_vol
        costThisTrade = price*vol

        if (vol+pre_vol) != 0:
            return (costPrevious+costThisTrade)/(vol+pre_vol)
        else:
            return 0

    def trade(self, stockNum, date, intent, vol, price=None, remarks=" "):
        if vol==0:
            logger.log(logging.WARNING, "Some logic error here")
            return True

        stockData = self.stockData[stockNum]

        if price==None:
            price = stockData.getOpenPrice(date)

        if price>stockData.getMaxPrice(date) or price<stockData.getMinPrice(date):
             logger.log(logging.WARNING, "Trade price out of range")
             price = stockData.getOpenPrice(date)

        if intent=="sell" or intent=="bearishSell":
            vol = -vol

        # check if out of range, sell/buy all
        if vol+self.data[stockNum].tradeSummary["Volume"]<0:
            if self.data[stockNum].tradeSummary["Volume"]==0:
                return False

            vol = -self.data[stockNum].tradeSummary["Volume"]
            remarks = "Out of range"

        # min trade unit = 1000 in tw, round vol
        vol = round(vol/CONFIG.TradingPara.tradeUnit)*CONFIG.TradingPara.tradeUnit        

        if self.stockData[stockNum].chkCanTrade(intent, date)==TRADE_ALLOWED:
            logger.log(logging.TRADE, str(stockNum) + ": " + date + " " + intent + " " + str(abs(vol)) + " at $" + str(price) + ", total $" + str(abs(price*vol)))
            self.__append(stockNum, date, intent, price, vol, remarks)

            # update budget
            self.myBudget.remainMoney -= (vol * price)
            return True

        else:
            return False

    def __tradingLoss(self, intent, vol, price):
        tradeMoney = vol*price

        if intent=="buy":
            fees = tradeMoney * CONFIG.TradingPara.fees
            if fees<20:
                fees = 20
            loss = fees
            logger.log(logging.TRADE, "Fees: " + str(fees))


        elif intent=="sell":
            fees = -tradeMoney * CONFIG.TradingPara.fees
            if fees<20:
                fees = 20
            tax = -tradeMoney * CONFIG.TradingPara.tax
            loss = fees + tax
            logger.log(logging.TRADE, "Fees: " + str(fees))
            logger.log(logging.TRADE, "Tax: " + str(tax))

        elif intent=="bearishBuy":
            #++
            fees = tradeMoney * CONFIG.TradingPara.fees
            if fees<20:
                fees = 20
            loss = fees
            logger.log(logging.TRADE, "Fees: " + str(fees))

        elif intent=="bearishSell":
            #++
            fees = -tradeMoney * CONFIG.TradingPara.fees
            if fees<20:
                fees = 20
            tax = -tradeMoney * CONFIG.TradingPara.tax
            loss = fees + tax
            logger.log(logging.TRADE, "Fees: " + str(fees))
            logger.log(logging.TRADE, "Tax: " + str(tax))

        return loss

    def checkout(self, stockNum, date, price, remarks="Check out"):
        logger.info(stockNum + ": Check Out")

        vol = (self.data[stockNum].tradeSummary)["Volume"]
        if vol > 0:
            intent = "sell"
        elif vol < 0:
            intent = "buy"

        if vol!=0:
            self.trade(stockNum, date, intent, vol, remarks=remarks)

    def saveResult(self, path):

        for stockNum in self.data:
            filePath = path + "/" + stockNum

            if not os.path.exists(filePath):
                os.makedirs(filePath)

            # trade history
            tradeHistory = self.data[stockNum].tradeHistory
            tradeHistory = [tradeHistory["buy"], tradeHistory["sell"], tradeHistory["bearishBuy"], tradeHistory["bearishSell"]]
            tradeHistory = pd.concat(tradeHistory)
            tradeHistory = tradeHistory.sort_index()
            tradeHistory.to_csv(filePath + "/trade history.csv", sep='\t', float_format='%.2f', index_label=False, mode='w')

            # trade summary
            logger.debug("Save File:" + filePath + "/trade summary.csv")
            self.data[stockNum].tradeSummary.to_csv(filePath + "/trade summary.csv", sep='\t', float_format='%.2f', index_label=False, mode='w')



