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


class ChannelGenerator(DataGenerator):
    def __init__(
            self,
            lower_capacity=Kbps(1000),
            upper_capacity=Kbps(10000),
            base_frequency_value=Kbps(4919500000),
            base_frequency_incrementation=Kbps(100000),
            seed=time.time()):
        self.lower_capacity = lower_capacity
        self.upper_capacity = upper_capacity
        self.base_frequency_value = base_frequency_value
        self.base_frequency_incrementation = base_frequency_incrementation

        random.seed(seed)
        numpy.random.seed(seed)

        self._validate()

    def generate(self, num_channels):
        data_file = open('../../../conf/data_generator.json')
        data = json.load(data_file)
        capacity_percentages = data['Channel Generator']['capacity']['percentages']
        capacity_ranges = data['Channel Generator']['capacity']['ranges']
        base_frequency_value = data['Channel Generator']['base_frequency']['value']
        base_frequency_incrementation = data['Channel Generator']['base_frequency']['incrementation']
        data_file.close()

        channels = []
        for i in range(0, num_channels):
            channels.append(Channel(
                frequency=Frequency(base_frequency_value +
                                    (i * base_frequency_incrementation)),
                capacity=Kbps(choice(self._generate_within_ranges(capacity_ranges), p=capacity_percentages))))
        return channels

    def generate_uniformly(self, num_channels):
        channels = []
        for x in range(num_channels):
            capacity = random.randint(
                self.lower_capacity.value, self.upper_capacity.value)
            channels.append(Channel(
                frequency=Frequency(
                    self.base_frequency_value.value + (x * self.base_frequency_incrementation.value)),
                capacity=Kbps(capacity)))

        return channels

    def _validate(self):
        if self.lower_capacity.value > self.upper_capacity.value:
            raise ChannelGeneratorRangeException('lower_capacity > upper_capacity, {0} > {1}'.format(
                self.lower_capacity.value, self.upper_capacity.value))
        if self.lower_capacity.value < 0:
            raise ChannelGeneratorRangeException(
                'lower_capacity < 0, {0}'.format(self.lower_capacity.value))
