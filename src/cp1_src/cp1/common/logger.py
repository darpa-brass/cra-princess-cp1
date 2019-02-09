"""

logger.py

Module that configured a singleton logger.
Author: Tameem Samawi (tsamawi@cra.com)

"""

import os
import sys
import datetime
import logging
from cp1.common.singleton import Singleton


class Logger(metaclass=Singleton):
    def __init__(self):
        """
        Logger object constructor
        """
        self.logger=logging.getLogger('logger')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        now = datetime.datetime.now()
        file_handler=logging.FileHandler('../../../logs/cp1_logger'+ now.strftime("%Y-%m-%d") +'.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
