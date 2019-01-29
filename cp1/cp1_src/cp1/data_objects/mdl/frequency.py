"""

frequency.py

Data object representing frequency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import FrequencyInitializationError


class Frequency:
    def __init__(self, value):
        """
        Constructor

        :param value: The frequency value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, int):
            raise FrequencyInitializationError(
                'Must be int: value {0}'.format(value),
                'Frequency.__init__')
        if value < 0:
            raise FrequencyInitializationError(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Frequency.__init__')
        self.value = value
