"""

txop_timeout.py

Data object representing timeout. According to Mdl documentation, this value must be in the range of [0, 255].
https://git.isis.vanderbilt.edu/SwRI/mdl-archive/blob/master/spec/MDL_v1_0_0.xsd
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import TxOpTimeoutInitializationError


class TxOpTimeout:
    def __init__(self, value):
        """
        Constructor

        :param value: The TxOp timeout value.
        :type value: int
        """
        if not isinstance(value, int):
            raise TxOpTimeoutInitializationError(
                'Must be int: value {0}'.format(value),
                'TxOpTimeout.__init__')
        if value < 0 or value > 255:
            raise TxOpTimeout(
                'Must be between 0 and 255: value {0}'.format(value),
                'TxOpTimeout.__init__')
        self.value = value
