"""channel.py

Data object representing a radio channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.kbps import Kbps


class Channel:
    def __init__(self, frequency, length, latency, capacity, constraints_object=None):
        """
        Constructor

        :param Frequency frequency: The frequency this channel sends data over.
        :param Milliseconds length: The total time over which the channel can schedule TAs. Equal to epoch.
        :param Milliseconds latency: Required delay between each transmisison for any TA.
        :param Kbps capacity: Throughput capacity. [1Mbps, 10Mbps]
        """
        if constraints_object is not None:
                def _create_channels(self, constraint):
                    """Transforms list of type int to list of type Channel.

                    :param pyorient.otypes.OrientRecord constraint: A Constraints OrientRecord
                    :returns List[Channel]: A list of channels constructed from constraints.available_frequencies
                    """
                    channels = []
                    for i in constraint.available_frequencies:
                        channels.append(Channel(frequency=Frequency(constraint.available_frequencies[i]),
                                                length=Milliseconds(constraint.epoch/1000),
                                                latency=Milliseconds(constraint.latency/1000),
                                                capacity=Kbps(constraint.channel_capacity*1000)))
                    return channels
        self.frequency = frequency
        self.length = length
        self.latency = latency
        self.capacity = capacity

        self.num_partitions = int(length.value / latency.value)
        self.partition_length = self.length.value / self.num_partitions
        self.first_available_time = 0
        self.value = 0

    def __str__(self):
        return '<Frequency: {0}, ' \
               'Length: {1}, ' \
               'Latency: {2}, ' \
               'Capacity: {3}, ' \
               'Num Partitions: {4}, ' \
               'Partition Length: {5}, ' \
               'First available time: {6}, '\
               'Value: {7}'.format(
               self.frequency,
               self.length,
               self.latency,
               self.capacity,
               self.num_partitions,
               self.partition_length,
               self.first_available_time,
               self.value
               )

    def __eq__(self, other):
        if isinstance(other, Channel):
            return (self.frequency == other.frequency and
                    self.length == other.length and
                    self.latency == other.latency and
                    self.capacity == other.capacity and
                    self.num_partitions == other.num_partitions and
                    self.partition_length == other.partition_length and
                    self.first_available_time == other.first_available_time and
                    self.value == other.value)
        return False

    __repr__ = __str__
