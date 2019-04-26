"""bandwidth_rate.py

Data object representing a new bandwidth value for voice, safety, bulk or RFNM.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.kbps import Kbps


class BandwidthRate:
    def __init__(self, type_, rate):
        """
        Constructor

        :param BandwidthTypes type_: The bandwidth type.
        :param int bandwidth_rate: The bandwidth rate.
        """
        self.type_ = type_
        self.rate = rate

    def __str__(self):
        return 'type_: {0}, value: {1}'.format(self.type_, self.rate.value)

    def __eq__(self, other):
        if isinstance(other, BandwidthRate):
            return self.type_ == other.type_ and self.rate == other.rate
        return False
