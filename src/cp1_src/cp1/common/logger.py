"""logger.py

Module that configures a singleton logger.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import os
import sys
import datetime
import logging
from pathlib import Path
from cp1.common.singleton import Singleton


class Logger(metaclass=Singleton):
    def __init__(self):
        """Logger object constructor.
        Logger is configured to output to a file and to the console.
        Files are outputted to the cp1/logs directory with a timestamp as follows:
        ``cp1_logger-YYYY-mm-dd.log``
        ``i.e. cp1_logger-2019-03-12.log``
        """
        self.#logger =logging.getLogger('logger')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        now = datetime.datetime.now()
        logs_path = str(Path(__file__).resolve().parents[3]) + '\/logs'
        file_handler = logging.FileHandler(
            filename=logs_path + now.strftime("-%Y-%m-%d") + '.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
