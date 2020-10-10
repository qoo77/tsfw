import logging
logger = logging.getLogger(__name__)

import importlib


class Algorithm(object):
    def __init__(self, fileName):
        logger.info("Init algorithm ")

        self.__importAlgorithm(fileName)
        self.__asignAlgorithm()
        

    def __importAlgorithm(self, fileName):
        try:
            self.algorithm = importlib.import_module("tsfw.algorithm." + fileName)
            logger.info("Load algorithm: " + fileName)

        except:
            logger.error("Load algorithm fail: " + fileName)
            raise Exception('No algorithm: ' + fileName)

    def __asignAlgorithm(self):
        # todo: assign function pointer here
        # todo: design function in algorithm_template
        # ex: self.tradeAlg = self.algorithm.tradeAlg , etc.
        pass

if __name__ == '__main__':
    algorithm = Algorithm("algorithm_template")