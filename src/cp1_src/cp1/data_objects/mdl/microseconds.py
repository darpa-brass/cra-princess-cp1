"""

microseconds.py

Data object representing microseconds.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import MicrosecondsInitializationException


class Microseconds:
    def __init__(self, value):
        """
        Constructor

        :param value: The microsecond value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, (int, float)):
            raise MicrosecondsInitializationException(
                'Must be int or float:\nvalue: {0}\ntype: {1}'.format(value, type(value)),
                'Microseconds.__init__')
        if value < 0:
            raise MicrosecondsInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Microseconds.__init__')
        self.value = value

    def toSeconds(self):
        return self.value / 1000000

    def toMilliseconds(self):
        return self.value / 1000

    def __str__(self):
        return str(self.value)
