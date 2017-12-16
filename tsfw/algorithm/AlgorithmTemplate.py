import logging
logger = logging.getLogger(__name__)

class Algorithm():
	#name = None
	def __init__(self):
		print("Algorithm1 create")
		pass

	def training(self, stockData):
		print("training") 
		raise Exception('Training Algorithm Not Emplement') 



	def testing(self, stockData):
		print("testing")
		raise Exception('testing Algorithm Not Emplement') 
		