import pandas as pd
import logging
logger = logging.getLogger(__name__)

class Algorithm():
	def __init__(self, tsfw):
		self.portfolios = tsfw.portfolios
		self.tsfw = tsfw
		self.bf = tsfw.bf
		
	
	def splitData(self, stockData):
		# All data testing, no training data
		stockData.splitData(None, "AllTest")

	def test_prework_stock(self, stockNum):

		statistics = self.tsfw.statistics
		stockData = self.tsfw.stockData[stockNum].data

		# calc BBANDS	
		statistics.load_Talib_BBANDS(stockNum, stockData, timeperiod=20)
		
		# add in plot queue
		self.tsfw.plot.addPlot2Queue(stockNum, 
										statistics.data[stockNum]["bbands"], 
										colName="upperband", 
										lineName="BBANDS upper")
		self.tsfw.plot.addPlot2Queue(stockNum, 
										statistics.data[stockNum]["bbands"],  
										colName="middleband", 
										lineName="BBANDS middle")
		self.tsfw.plot.addPlot2Queue(stockNum, 
										statistics.data[stockNum]["bbands"],
										colName="lowerband", 
										lineName="BBANDS lower")

	def test_prework(self):
		pass

	def test_strategy(self, stockNum, today, yesterday):

		if self.bf.isIntersect(yesterday, 
							self.tsfw.stockData[stockNum].testingData, 
							"ClosePrice", 
							self.tsfw.statistics.data[stockNum]["bbands"], 
							"lowerband", 
							line1Low2High=True,  
							continuedDate=1):
			self.portfolios.trade(stockNum, today, "buy", 1000)


		elif self.bf.isIntersect(yesterday, 
							self.tsfw.stockData[stockNum].testingData, 
							"ClosePrice", 
							self.tsfw.statistics.data[stockNum]["bbands"], 
							"upperband", 
							line1Low2High=False,  
							continuedDate=1):
			self.portfolios.trade(stockNum, today, "sell", 1000)


	def test_dateSummary(self, date):
		pass

	def test_afterwork_stock(self, stockNum, date):
		price = self.tsfw.stockData[stockNum].getClosePrice(date)
		self.portfolios.checkout(stockNum, date, price)
		pass

	def test_afterwork(self):
		pass


	def train(self):
		pass
