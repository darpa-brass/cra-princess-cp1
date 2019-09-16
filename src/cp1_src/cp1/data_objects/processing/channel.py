"""channel.py

Data object representing a radio channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.kbps import Kbps
from cp1.utils.decorators.timedelta import timedelta


class Channel:
    def __init__(self, frequency, capacity):
        """
        Constructor

        :param Frequency frequency: The frequency this channel sends data over.
        :param Kbps capacity: Throughput capacity. Range is from 1Mbps to 10Mbps inclusive.
        """
        self.frequency = frequency
        self.capacity = capacity

        self.start_time = timedelta(microseconds=0)
        self.value = 0

    def __str__(self):
        return 'frequency: {0}, ' \
               'capacity: {1}, ' \
               'start_time: {2}, '\
               'value: {3}'.format(
                   self.frequency,
                   self.capacity,
                   self.start_time.get_microseconds(),
                   self.value
               )

    def __eq__(self, other):
        if isinstance(other, Channel):
            return self.frequency.value == other.frequency.value
        return False

    def __hash__(self):
      return hash(self.frequency.value)

    __repr__ = __str__
