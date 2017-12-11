import pandas as pd

class Algorithm():
	def __init__(self, tsfw):
		print("Algorithm1 create")
		self.portfolios = tsfw.portfolios
		self.tsfw = tsfw
		self.bf = tsfw.baseFunction
		
	
	def splitData(self, stockData):
		# All data testing, no training data
		stockData.splitData(None, "AllTest")

	def test_prework_stock(self, stockNum):

		statistics = self.tsfw.statistics
		stockData = self.tsfw.stockData[stockNum].data

		# calc BBANDS	
		if not statistics.chkTAExist(stockNum, "bbands"):
			df = pd.DataFrame(stockData["ClosePrice"])
			df.rename(columns={'ClosePrice': 'close'}, inplace=True)

			# upper, mid lower band
			statistics.data[stockNum]["bbands"] = statistics.taFunc("bbands")(df, timeperiod=20, nbdevup=2, nbdevdn=2, matype=statistics.MA_Type.SMA)
	
			# %b (pb), def:(close-lower)/(upper-lower) 
			statistics.data[stockNum]["bbands"]["pb"] = (stockData["ClosePrice"] - statistics.data[stockNum]["bbands"]["lowerband"])/(statistics.data[stockNum]["bbands"]["upperband"] - statistics.data[stockNum]["bbands"]["lowerband"])

			# BW, def:(upper-lower)/middle
			statistics.data[stockNum]["bbands"]["bw"] = (statistics.data[stockNum]["bbands"]["upperband"] - statistics.data[stockNum]["bbands"]["lowerband"])/statistics.data[stockNum]["bbands"]["middleband"]

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
			self.portfolios.trade(stockNum, 
									today, 
									"buy", 
									self.tsfw.stockData[stockNum].getOpenPrice(today), 
									1000)


		elif self.bf.isIntersect(yesterday, 
							self.tsfw.stockData[stockNum].testingData, 
							"ClosePrice", 
							self.tsfw.statistics.data[stockNum]["bbands"], 
							"upperband", 
							line1Low2High=False,  
							continuedDate=1):
			self.portfolios.trade(stockNum, 
									today, 
									"sell", 
									self.tsfw.stockData[stockNum].getOpenPrice(today), 
									1000)


	def test_dateSummary(self, date):
		pass

	def test_afterwork_stock(self, stockNum):
		pass

	def test_afterwork(self):
		pass


	def train(self):
		print("train")  
