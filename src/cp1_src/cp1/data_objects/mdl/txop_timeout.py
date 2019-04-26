"""txop_timeout.py

Data object representing timeout. Must be in the range of [0, 255].
`MDL Documentation <https://git.isis.vanderbilt.edu/SwRI/mdl-archive/blob/master/spec/MDL_v1_0_0.xsd>`_.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import TxOpTimeoutInitializationException


class TxOpTimeout:
    def __init__(self, value):
        """
        Constructor

        :param int value: The TxOp timeout value.
        """
        if value < 0 or value > 255:
            raise TxOpTimeoutInitializationException(
                'Must be between 0 and 255. value: {0}'.format(value),
                'TxOpTimeout.__init__')
        self.value = value

    def __str__(self):
        return ('TxOpTimeout: {0}'.format(self.value))

    def __eq__(self, other):
        if isinstance(other, TxOpTimeout):
            return self.value == other.value
        return False
