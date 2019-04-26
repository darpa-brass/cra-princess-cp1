"""microseconds.py

Data object representing microseconds.
Author: Tameem Samawi (tsamawi@cra.com)
"""


class Microseconds:
    def __init__(self, value):
        """
        Constructor

        :param int value: The microsecond value. Must be greater than 0.
        """
        self.value = value

    def in_seconds(self):
        return self.value / 1000000

    def in_milliseconds(self):
        return self.value / 1000

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Microseconds):
            return self.value == other.value
        return False
