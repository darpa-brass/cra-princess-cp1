"""

mdl_frequency_test.py

Module to test frequency.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.mdl.frequency import Frequency
from cp1.common.exception_class import FrequencyInitializationError


class MDLFrequencyTest(unittest.TestCase):
    def test_valid_frequency(self):
        value = 491950000
        frequency = Frequency(value)
        self.assertEquals(value, frequency.value)

    def test_incorrect_frequency_value_negative(self):
        self.assertRaises(
            FrequencyInitializationError,
            Frequency,
            -1)

    def test_incorrect_frequency_value_type(self):
        self.assertRaises(
            FrequencyInitializationError,
            Frequency,
            'foo')
