import random
import json
import numpy
import time
from numpy.random import choice
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.channel import Channel
from cp1.utils.data_generator import DataGenerator
from cp1.common.exception_class import ChannelGeneratorRangeException
from cp1.utils.json_utils import extract_percentages


class ChannelGenerator(DataGenerator):
    def __init__(self, config_file):
        """
        :param str config_file: The path to the JSON file containing generation data.
        """
        self.config_file = config_file
    def generate(self):
        """
        Generates a set amount of Channels in the range of data provided by data_file.
        """
        self._extract_data()
        self._validate()
        channels = []
        for i in range(0, self.num_channels):
            channels.append(Channel(
                frequency=Frequency(self.base_frequency[0] +
                                    (i * self.base_frequency[1])),
                capacity=Kbps(choice(self._generate_within_ranges(self.capacity), p=extract_percentages(self.capacity)))))
        return channels

    def _extract_data(self):
        """
        Attempts to open extract the values from data_file_path.
        """
        with open(self.config_file) as f:
            data = json.load(f)
            try:
                self.num_channels = data['Channels']['num_channels']
                self.seed = data['Channels']['seeds']
                self.base_frequency= data['Channels']['base_frequency']
                self.capacity = data['Channels']['capacity']
            except Exception as ex:
                raise ConfigFileException(ex, 'ChannelGenerator._extract_data')

    def _validate(self):
        """
        Validates that the data is in the correct places.
        """
        self.validate_base_frequency(self.base_frequency)
        self.validate_seeds(self.seed)
        self.validate_num_to_generate('num_channels', self.num_channels)
        self.validate_distribution_schema('capacity', self.capacity)
