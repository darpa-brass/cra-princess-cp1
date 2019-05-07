"""scheduled_ta.py

Data object representing a TA that has been selected for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.processing import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.mdl.kbps import Kbps


class ScheduledTA:
    def __init__(self, ta, bandwidth, channel):
        """
        :param TA ta: The TA to be scheduled.
        :param Kbps bandwidth: The bandwidth to assign this TA.
        :param Channel channel: The channel this TA is to be scheduled on.
        """
        self.ta = ta
        self.bandwidth = bandwidth
        self.channel = channel

    def __str__(self):
        return 'ta: {0}, bandwidth: {1}, channel: {2}'.format(self.ta, self.bandwidth, self.channel)

    __repr__ = __str__
