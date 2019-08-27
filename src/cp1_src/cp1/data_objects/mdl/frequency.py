"""frequency.py

Data object representing frequency.
Author: Tameem Samawi (tsamawi@cra.com)
"""


class Frequency:
    def __init__(self, value):
        """
        Constructor

        :param int value: The frequency value. Must be greater than 0.
        """
        if value < 0:
            raise FrequencyInitializationException(
                'Must be greater than or equal to zero: value {0}'.format(
                    value),
                'Frequency.__init__')
        self.value = value

    def __str__(self):
        return 'frequency: {0}'.format(self.value)

    def __eq__(self, other):
        if isinstance(other, Frequency):
            return self.value == other.value
        return False

    __repr__ = __str__
