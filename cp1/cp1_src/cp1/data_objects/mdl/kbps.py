"""

kbps.py

Data object representing kbps.
Author: Tameem Samawi (tsamawi@cra.com)

"""
from cp1.common.exception_class import KbpsInitializationError


class Kbps:
    def __init__(self, value):
        """
        Constructor

        :param value: The Kbps value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, int):
            raise KbpsInitializationError(
                'Must be int: value {0}'.format(value),
                'Frequency.__init__')
        if value < 0:
            raise KbpsInitializationError(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Kbps.__init__')
        self.value = value
