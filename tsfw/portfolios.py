import pandas as pd
import os
#from numpy import isnan

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

    def __init__(self, tradingPara, myBudget):
        self.tradingPara = tradingPara
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
        #print(intent+ " price=" +str(price)+ " vol="+str(vol))
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

    def trade(self, stockNum, date, intent, price, vol, remarks=" "):
        #print("trade-> " + intent + " " + str(vol))
        if vol==0:
            return True
        #if isnan(price):
        #	return False

        if intent=="sell" or intent=="bearishSell":
            vol = -vol

        # check if out of range, sell/buy all
        if vol+self.data[stockNum].tradeSummary["Volume"]<0:
            vol = -self.data[stockNum].tradeSummary["Volume"]
            remarks = "Out of range"

        # min trade unit = 1000 in tw, round vol
        vol = round(vol/self.tradingPara.tradeUnit)*self.tradingPara.tradeUnit



        if self.__chkCanTrade(intent):
            self.__append(stockNum, date, intent, price, vol, remarks)

            # update budget
            self.myBudget.remainMoney -= (vol * price)
            return True

        else:
            return False

    def __chkCanTrade(self, intent):
        #print("chkCanTrade")
        # check 7% or 10% by date ++
        # 金融監督管理委員會宣布自104年 6月1日起，將漲跌幅度由7%放寬為10%
        ret=False
        if intent=="buy":
            #++
            ret=True
        elif intent=="bearishBuy":
            #++
            if bool(self.tradingPara.canBearish):
                ret=True
        elif intent=="sell":
            #++
            ret=True
        elif intent=="bearishSell":
            #++
            if bool(self.tradingPara.canBearish):
                ret=True

        return ret

    def __tradingLoss(self, intent, vol, price):
        #print("tradingFees")
        tradeMoney = vol*price

        if intent=="buy":
            loss = tradeMoney * self.tradingPara.fees
            if loss<20:
                loss = 20
        elif intent=="sell":
            loss = -tradeMoney * self.tradingPara.fees
            if loss<20:
                loss = 20
            loss += (-tradeMoney * self.tradingPara.tax)

        elif intent=="bearishBuy":
            #++
            loss = tradeMoney * self.tradingPara.fees
            if loss<20:
                loss = 20

        elif intent=="bearishSell":
            #++
            loss = -tradeMoney * self.tradingPara.fees
            if loss<20:
                loss = 20
            loss += (-tradeMoney * self.tradingPara.tax)

        return loss

    def checkout(self, stockNum, date, price, remarks="Check out"):
        print("checkOut")

        vol = (self.data[stockNum].tradeSummary)["Volume"]
        if vol > 0:
            intent = "sell"
        elif vol < 0:
            intent = "buy"

        if vol!=0:
            self.trade(stockNum, date, intent, price, vol, remarks)

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
            self.data[stockNum].tradeSummary.to_csv(filePath + "/trade summary.csv", sep='\t', float_format='%.2f', index_label=False, mode='w')



