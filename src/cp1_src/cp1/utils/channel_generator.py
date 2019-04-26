import random
import json
from numpy.random import choice
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.channel import Channel
from cp1.utils.data_generator import DataGenerator
from cp1.common.exception_class import ChannelGeneratorRangeException

class ChannelGenerator(DataGenerator):
    def __init__(self, lower_length=Milliseconds(1), upper_length=Milliseconds(1), lower_latency=Milliseconds(1), upper_latency=Milliseconds(1),
                    lower_capacity=Kbps(1000), upper_capacity=Kbps(10000), seeded=False):
        self.lower_length = lower_length
        self.upper_length = upper_length
        self.lower_latency = lower_latency
        self.upper_latency = upper_latency
        self.lower_capacity = lower_capacity
        self.upper_capacity = upper_capacity
        self.seeded = seeded

        self._validate()

    def generate(self, num_channels):
        data_file = open('../../../../conf/data_generator.json', 'r')
        data = json.load(data_file)
        capacity_percentages = data['Channel Generator']['capacity']['percentages']
        capacity_ranges = data['Channel Generator']['capacity']['ranges']
        data_file.close()

        # Delete below once complete
        length = 1
        frequency = 1
        latency = 1
        # Delete above once complete
        channels = []
        for i in range(0, num_channels):
            channels.append(Channel(
                                # Delete below once complete
                                Frequency(frequency),
                                Milliseconds(length),
                                Milliseconds(latency),
                                # Delete above once complete
                                Kbps(choice(self._generate_within_ranges(capacity_ranges), p=capacity_percentages))))
        return channels

    def generate_uniformly(self, num_channels):
        if(self.seeded):
            random.seed(1)

        channels = []
        frequency = 4919500000
        for x in range(num_channels):
            length = random.randint(self.lower_length.value, self.upper_length.value)
            latency = random.randint(self.lower_latency.value, self.upper_latency.value)
            capacity = random.randint(self.lower_capacity.value, self.upper_capacity.value)

            channels.append(Channel(Frequency(frequency), Milliseconds(length),
                            Milliseconds(latency), Kbps(capacity)))
            frequency += 100000
        self.channels = channels

    def _validate(self):
        if self.lower_length.value < self.lower_latency.value:
            raise ChannelGeneratorRangeException('lower_length < lower_latency, {0} > {1}'.format(self.lower_length.value, self.lower_latency.value))
        if self.upper_length.value < self.upper_latency.value:
            raise ChannelGeneratorRangeException('upper_length < upper_latency, {0} > {1}'.format(self.upper_length.value, self.upper_latency.value))
        if self.lower_length.value > self.upper_length.value:
            raise ChannelGeneratorRangeException('lower_length > upper_length, {0} > {1}'.format(self.lower_length.value, self.upper_length.value))
        if self.lower_latency.value > self.upper_latency.value:
            raise ChannelGeneratorRangeException('lower_latency > upper_latency, {0} > {1}'.format(self.lower_latency.value, self.upper_latency.value))
        if self.lower_capacity.value > self.upper_capacity.value:
            raise ChannelGeneratorRangeException('lower_capacity > upper_capacity, {0} > {1}'.format(self.lower_capacity.value, self.upper_capacity.value))
        if self.lower_length.value <= 0:
            raise ChannelGeneratorRangeException('lower_length < 0, {0}'.format(self.lower_length.value))
        if self.lower_latency.value < 0:
            raise ChannelGeneratorRangeException('lower_latency < 0, {0}'.format(self.lower_latency.value))
        if self.lower_capacity.value < 0:
            raise ChannelGeneratorRangeException('lower_capacity < 0, {0}'.format(self.lower_capacity.value))

channel_generator = ChannelGenerator()
num = 100
channel_generator.generate(num)
