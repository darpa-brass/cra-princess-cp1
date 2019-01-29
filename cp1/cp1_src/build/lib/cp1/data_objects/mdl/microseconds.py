"""

microseconds.py

Data object representing microseconds.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import MicrosecondsInitializationError


class Microseconds:
    def __init__(self, value):
        """
        Constructor

        :param value: The microsecond value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, int):
            raise MicrosecondsInitializationError(
                'Must be int: value {0}'.format(value),
                'Microseconds.__init__')
        if value < 0:
            raise MicrosecondsInitializationError(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Microseconds.__init__')
        self.value = value

    def toSeconds(self):
        return self.value / 1000000
