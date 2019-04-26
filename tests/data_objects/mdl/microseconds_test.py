"""
microseconds_test.py

Module to test microseconds.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.common.exception_class import MicrosecondsInitializationException


class MicrosecondsTest(unittest.TestCase):
    def test_valid_microseconds(self):
        value = 10000
        microseconds = Microseconds(value)
        self.assertEqual(value, microseconds.value)

    def test_invalid_microseconds_value_negative(self):
        self.assertRaises(
            MicrosecondsInitializationException,
            Microseconds,
            -1000)

    def test_invalid_microseconds_value_type(self):
        self.assertRaises(
            MicrosecondsInitializationException,
            Microseconds,
            'Foo')

    def test_in_seconds_0(self):
        microsecond = Microseconds(0)
        self.assertEqual(0, microsecond.inSeconds())

    def test_in_seconds_12500(self):
        microsecond = Microseconds(12500)
        self.assertEqual(.0125, microsecond.inSeconds())

    def test_in_milliseconds_0(self):
        microsecond = Microseconds(0)
        self.assertEqual(0, microsecond.inMilliseconds())

    def test_in_milliseconds_1250000(self):
        microsecond = Microseconds(12500000)
        self.assertEqual(12500, microsecond.inMilliseconds())

    def test___eq__(self):
        m1 = Microseconds(1000)
        m2 = Microseconds(1000)

        self.assertTrue(m1 == m2)
