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
    def __init__(self):
        self._extract_data()
        self._validate()

    def generate(self):
        channels = []
        for i in range(0, self.num_channels):
            channels.append(Channel(
                frequency=Frequency(self.base_frequency[0] +
                                    (i * self.base_frequency[1])),
                capacity=Kbps(choice(self._generate_within_ranges(self.capacity), p=extract_percentages(self.capacity)))))
        return channels

    def _extract_data(self):
        data_file = open('C:/dev/cp1/conf/data.json')
        data = json.load(data_file)
        try:
            self.num_channels = data['Channels']['num_channels']
            self.seed = data['Channels']['seeds']
            self.base_frequency= data['Channels']['base_frequency']
            self.capacity = data['Channels']['capacity']
        except Exception as ex:
            raise ConfigFileException(ex, 'ChannelGenerator._extract_data')
        data_file.close()

    def _validate(self):
        if not isinstance(self.base_frequency[0], int) or self.base_frequency[0] < 0:
            raise ConfigFileException(
                'Base Frequency ({0}) must be an int greater than 0'.format(self.base_frequency[0]))
        if not isinstance(self.base_frequency[1], int):
            raise ConfigFileException(
                'Incrementation ({0}) must be an int'.format(self.base_frequency[1]))
        self.validate_seeds(self.seed)
        self.validate_num_to_generate('num_channels', self.num_channels)
        self.validate_distribution_schema('capacity', self.capacity)
