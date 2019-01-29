"""

millisecond_test.py

Module to test millisecond.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.common.exception_class import MillisecondsInitializationError


class MillisecondsTest(unittest.TestCase):
    def test_valid_millisecond(self):
        value = 10000
        millisecond = Milliseconds(value)
        self.assertEqual(value, millisecond.value)

    def test_invalid_millisecond_value_negative(self):
        self.assertRaises(
            MillisecondsInitializationError,
            Milliseconds,
            -1000)

    def test_invalid_millisecond_value_type(self):
        self.assertRaises(
            MillisecondsInitializationError,
            Milliseconds,
            'Foo')

    def test_to_seconds_0(self):
        millisecond = Milliseconds(0)
        self.assertEqual(0, millisecond.toSeconds())

    def test_to_seconds_positive_int(self):
        millisecond = Milliseconds(1250)
        self.assertEqual(1.25, millisecond.toSeconds())
