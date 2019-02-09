"""

bandwidth_rate.py

Data object representing a new bandwidth value for voice, safety, bulk or RFNM.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import BandwidthRateInitializationException
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.kbps import Kbps


class BandwidthRate:
    def __init__(self, bandwidth_type, rate):
        """
        Constructor

        :param bandwidth_type: The bandwidth type.
        :type bandwidth_type: BandwidthTypes

        :param bandwidth_rate: The bandwidth rate.
        :type bandwidth_rate: int
        """
        if not isinstance(bandwidth_type, BandwidthTypes):
            raise BandwidthRateInitializationException(
                'bandwidth_type be instance of BandwidthTypes:\nvalue: {0}\ntype: {1}'.format(bandwidth_type, type(bandwidth_type)),
                'BandwidthRate.__init__')
        if not isinstance(rate, Kbps):
            raise BandwidthRateInitializationException(
                'rate must be instance of Kbps:\nvalue: {0}\ntype: {1}'.format(rate, type(rate)),
                'BandwidthRate.__init__')

        self.bandwidth_type = bandwidth_type
        self.rate = rate

    def __str__(self):
        return 'bandwidth_type: {0}, value: {1}'.format(self.bandwidth_type, self.rate.value)
