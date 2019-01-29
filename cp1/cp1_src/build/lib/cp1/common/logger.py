"""

logger.py

Module that configured a singleton logger.
Author: Tameem Samawi (tsamawi@cra.com)

"""

from cp1.common.singleton import Singleton
import datetime
import logging


class Logger(metaclass=Singleton):
    def __init__(self):
        """
        Logger object constructor
        """
        self.logger=logging.getLogger('logger')
        self.logger.setLevel(logging.DEBUG)
        now = datetime.datetime.now()
        # handler=logging.FileHandler('../../../logs/scenario_logger'+ now.strftime("%Y-%m-%d") +'.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # handler.setFormatter(formatter)
        # self.logger.addHandler(handler)
