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
        self.logger = logging.getLogger('logger')
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def setup_file_handler(self, logging_dir):
        """Sets the handler of this class to be a filehandler which outputs to the logging_dir folder.

        :param str logging_dir: The directory where logs should be output
        """
        now = datetime.datetime.now()
        file_handler = logging.FileHandler(
            filename= logging_dir + 'cp1_logger' + now.strftime("-%Y-%m-%d") + '.log')
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
