"""

frequency.py

Data object representing frequency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import FrequencyInitializationException


class Frequency:
    def __init__(self, value):
        """
        Constructor

        :param value: The frequency value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, int):
            raise FrequencyInitializationException(
                'Must be int:\nvalue: {0}\ntype: {1}'.format(value, type(value)),
                'Frequency.__init__')
        if value < 0:
            raise FrequencyInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Frequency.__init__')
        self.value = value

    def __str__(self):
        return 'frequency: {0}'.format(self.value)
