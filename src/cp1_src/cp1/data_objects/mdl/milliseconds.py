"""

millisecond.py

Data object representing milliseconds.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import MillisecondsInitializationException


class Milliseconds:
    def __init__(self, value):
        """
        Constructor

        :param value: The millisecond value. Must be greater than 0.
        :type value: int
        """
        if not isinstance(value, (int, float)):
            raise MillisecondsInitializationException(
                'Must be int or float:\nvalue: {0}\ntype: {1}'.format(value, type(value)),
                'Milliseconds.__init__')
        if value < 0:
            raise MillisecondsInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(value),
                'Milliseconds.__init__')
        self.value = value

    def toSeconds(self):
        return self.value / 1000

    def __str__(self):
        return str(self.value)
