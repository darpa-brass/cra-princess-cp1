"""

kbps.py

Data object representing kbps.
Author: Tameem Samawi (tsamawi@cra.com)

"""
from cp1.common.exception_class import KbpsInitializationException


class Kbps:
    def __init__(self, value):
        """
        Constructor

        :param value: The Kbps value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, (int, float)):
            raise KbpsInitializationException(
                'Must be int or float: value {0}'.format(value),
                'Frequency.__init__')
        if value < 0:
            raise KbpsInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Kbps.__init__')
        self.value = value

    def to_bits_per_second(self):
        return self.value * 1000

    def __str__(self):
        return 'Kbps: {0}'.format(self.value)
