import pandas as pd
import logging
logger = logging.getLogger(__name__)

class Algorithm():
	#for plot debug
	def __init__(self, tsfw):
		print("Algorithm1 create")
		self.portfolios = tsfw.portfolios
		self.tsfw = tsfw
		self.bf = tsfw.baseFunction
		
	
	def splitData(self, stockData):
		# All data testing, no training data
		stockData.splitData(None, "AllTest")

	def test_prework_stock(self, stockNum):

		pass

	def test_prework(self):
		pass

	def test_strategy(self, stockNum, today, yesterday):
		
		#debug alg
		
		if today[8:]=="01":
			self.portfolios.trade(stockNum, 
									today, 
									"buy", 
									self.tsfw.stockData[stockNum].getOpenPrice(today), 
									1000)
		#else:
		#	self.portfolios.trade(stockNum, date, "sell",self.tsfw.stockData[stockNum].getOpenPrice(date), 1000)
		
		pass

	def test_dateSummary(self, date):
		pass

	def test_afterwork_stock(self, stockNum):
		pass

	def test_afterwork(self):
		pass


	def train(self):
		print("train")  
