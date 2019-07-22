"""milliseconds.py

Data object representing milliseconds.
Author: Tameem Samawi (tsamawi@cra.com)
"""


class Milliseconds:
    def __init__(self, value):
        """
        Constructor

        :param int value: The millisecond value. Must be greater than 0.
        """
        self.value = value

    def in_seconds(self):
        return self.value / 1000

    def in_microseconds(self):
        return self.value * 1000

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Milliseconds):
            return self.value == other.value
        return False
