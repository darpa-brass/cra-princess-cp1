"""channel.py

Data object representing a radio channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.kbps import Kbps


class Channel:
    def __init__(self, frequency=Kbps(4919500000), capacity=Kbps(10000)):
        """
        Constructor

        :param Frequency frequency: The frequency this channel sends data over.
        :param Kbps capacity: Throughput capacity. Range is from 1Mbps to 10Mbps inclusive.
        """
        self.frequency = frequency
        self.capacity = capacity

        self.first_available_time = 0
        self.value = 0

    def __str__(self):
        return 'Frequency: {0}, ' \
               'Capacity: {1}, ' \
               'First available time: {2}, '\
               'Value: {3}'.format(
                   self.frequency,
                   self.capacity,
                   self.first_available_time,
                   self.value
               )

    def __eq__(self, other):
        if isinstance(other, Channel):
            return (self.frequency == other.frequency and
                    self.capacity == other.capacity and
                    self.first_available_time == other.first_available_time and
                    self.value == other.value)
        return False

    __repr__ = __str__
