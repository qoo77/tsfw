from tsfw.const import*
import configparser

def init():
    global CONFIG
    CONFIG = load()


def load():
    configPath = "tsfw/config.ini"
    config = configparser.ConfigParser()
    config.read(configPath)

    try:
        configuration = lambda:0
        configuration.Path = lambda:0
        configuration.Path.dataDir = config.get("Path", "data dir")
        configuration.Path.outputDir = config.get("Path", "output dir")

        configuration.StockData = lambda:0
        configuration.StockData.organizeAndOverwriteData = False if config.get("StockData", "organize and overwrite data")=="0" else True
        configuration.StockData.dataSource = config.get("StockData", "data source")

        configuration.Budget = lambda:0
        configuration.Budget.money = int(config.get("Budget", "money"))

        configuration.Algorithm = lambda:0

        configuration.TradingPara = lambda:0
        configuration.TradingPara.market = config.get("Trading Para", "market")
        configuration.TradingPara.fees = float(config.get("Trading Para", "fees"))
        configuration.TradingPara.minFees = float(config.get("Trading Para", "min fees"))
        configuration.TradingPara.tax = float(config.get("Trading Para", "tax"))#only at sell
        configuration.TradingPara.canBearish = False if config.get("Trading Para", "tax")=="0" else True
        configuration.TradingPara.tradeUnit = int(config.get("Trading Para", "trade unit"))
    
        configuration.LogLevel = lambda:0
        configuration.LogLevel.logFile = int(config.get("Log Level", "log file"))
        configuration.LogLevel.commandLine = int(config.get("Log Level", "command line"))
    
        configuration.Debug = lambda:0
        configuration.Debug.debug = False if config.get("Debug", "debug")=="0" else True
        

    except:
        raise Exception('Wrong Config At ' + configPath)

    return configuration
