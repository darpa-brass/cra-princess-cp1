"""

bandwidth_value.py

Data object representing a new bandwidth value for voice, safety, bulk or RFNM.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import BandwidthValueInitializationException


class BandwidthValue:
    def __init__(self, bandwidth_type, value):
        """
        Constructor

        :param bandwidth_type: The bandwidth type.
        :type bandwidth_type: BandwidthTypes

        :param value: The bandwidth value.
        :type value: int
        """
        if not isinstance(value, Kbps):
            raise BandwidthValueInitializationException(
                'value must be instance of Kbps:\nvalue: {0}\ntype: {1}'.format(value, type(value)),
                'BandwidthValue.__init__')
        if not(type(bandwidth_type, BandwidthTypes)):
            raise BandwidthValueInitializationException(
                'bandwidth_type be instance of BandwidthTypes:\nvalue: {0}\ntype: {1}'.format(bandwidth_type, type(bandwidth_type)),
                'BandwidthValue.__init__')            
        if value < 0:
            raise BandwidthValueInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'BandwidthValue.__init__')
        self.value = value

    def __str__(self):
        return 'bandwidth_type: {0}, value: {1}'.format(self.bandwidth_type, self.value)

class BandwidthTypes(Enum):
    voice = 1
    safety = 2
    rfnm = 3
    bulk = 4
