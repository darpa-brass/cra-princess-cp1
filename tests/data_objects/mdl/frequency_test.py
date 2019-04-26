"""
frequency_test.py

Module to test frequency.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.frequency import Frequency
from cp1.common.exception_class import FrequencyInitializationException


class FrequencyTest(unittest.TestCase):
    def test_valid_frequency(self):
        frequency = Frequency(4919500000)
        self.assertEqual(4919500000, frequency.value)

    def test___eq__(self):
        f1 = Frequency(4919500000)
        f2 = Frequency(4919500000)
        self.assertTrue(f1 == f2)

    def test_incorrect_frequency_value_negative(self):
        self.assertRaises(
            FrequencyInitializationException,
            Frequency,
            -1)

    def test_incorrect_frequency_value_type(self):
        self.assertRaises(
            FrequencyInitializationException,
            Frequency,
            'foo')
