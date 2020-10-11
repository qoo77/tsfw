import logging
logger = logging.getLogger(__name__)

import configparser
from collections import namedtuple

def init(configName):
    gConfig = __loadConfig(configName)
    return gConfig

def __dict2Tuple(d):
    top = type('new', (object,), d)
    seqs = tuple, list, set, frozenset
    for i, j in d.items():
        if isinstance(j, dict):
            setattr(top, i, __dict2Tuple(j))
        elif isinstance(j, seqs):
            setattr(top, i, 
                type(j)(__dict2Tuple(sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(top, i, j)
    return top

def __loadConfig(configName):
    logger.info("Load config: " + configName)

    config = configparser.ConfigParser()

    try:
        config.read(configName)
    except:
        raise Exception('Wrong Config At ' + configName)

    configuration = config._sections

    # transform data tyoe in config
    for section in configuration.keys():
        for key in configuration[section]:
            # Transform string "yes" "true" to boolean True
            if configuration[section][key].lower() in ("yes", "true"):
                configuration[section][key] = True
            # Transform string "no" "false to bolean false"
            elif configuration[section][key] in ("no", "false"):
                configuration[section][key] = False
            # Transform string to int
            elif __isInt(configuration[section][key]):
                configuration[section][key] = int(configuration[section][key])
            # Transform string to float
            elif __isFloat(configuration[section][key]):
                configuration[section][key] = float(configuration[section][key])

    # Transform dict to tuple
    configuration = __dict2Tuple(configuration)

    return configuration

def __isFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def __isInt(str):
    return str.isnumeric()

def __createDefaultConfig():
    # todo: write default ini file
    """
    sample:
    with open('example.ini', 'w') as configfile:
    config.write(configfile)
    """
    pass