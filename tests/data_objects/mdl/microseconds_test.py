"""

microseconds_test.py

Module to test millisecond.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.common.exception_class import MicrosecondsInitializationError


class MicrosecondsTest(unittest.TestCase):
    def test_valid_millisecond(self):
        value = 10000
        millisecond = Microseconds(value)
        self.assertEqual(value, millisecond.value)

    def test_invalid_millisecond_value_negative(self):
        self.assertRaises(
            MicrosecondsInitializationError,
            Microseconds,
            -1000)

    def test_invalid_millisecond_value_type(self):
        self.assertRaises(
            MicrosecondsInitializationError,
            Microseconds,
            'Foo')

    def test_to_seconds_0(self):
        microsecond = Microseconds(0)
        self.assertEqual(0, microsecond.toSeconds())

    def test_to_seconds_positive_int(self):
        microsecond = Microseconds(12500)
        self.assertEqual(.0125, microsecond.toSeconds())
