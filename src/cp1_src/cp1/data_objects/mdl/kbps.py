"""kbps.py

Data object representing Kbps.
Author: Tameem Samawi (tsamawi@cra.com)
"""


class Kbps:
    def __init__(self, value):
        """
        Constructor

        :param int value: The Kbps value. Must be greater than 0.
        """
        if value < 0:
            raise KbpsInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(
                    value),
                'Kbps.__init__')
        self.value = value

    def in_bits_per_second(self):
        return self.value * 1000

    def in_megabits_per_second(self):
        return self.value / 1000

    def __str__(self):
        return 'Kbps: {0}'.format(self.value)

    def __eq__(self, other):
        if isinstance(other, Kbps):
            return self.value == other.value
        return False
