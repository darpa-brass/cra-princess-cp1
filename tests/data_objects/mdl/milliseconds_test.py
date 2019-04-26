"""
milliseconds_test.py

Module to test milliseconds.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.common.exception_class import MillisecondsInitializationException


class MillisecondsTest(unittest.TestCase):
    def test_valid_millisecond(self):
        value = 10000
        millisecond = Milliseconds(value)
        self.assertEqual(value, millisecond.value)

    def test_invalid_millisecond_value_negative(self):
        self.assertRaises(
            MillisecondsInitializationException,
            Milliseconds,
            -1000)

    def test_invalid_millisecond_value_type(self):
        self.assertRaises(
            MillisecondsInitializationException,
            Milliseconds,
            'Foo')

    def test_in_seconds_0(self):
        millisecond = Milliseconds(0)
        self.assertEqual(0, millisecond.inSeconds())

    def test_in_seconds_1250(self):
        millisecond = Milliseconds(1250)
        self.assertEqual(1.25, millisecond.inSeconds())

    def test_in_microseconds_0(self):
        millisecond = Milliseconds(0)
        self.assertEqual(0, millisecond.inMicroseconds())

    def test_in_microseconds_1250(self):
        millisecond = Milliseconds(1250)
        self.assertEqual(1250000, millisecond.inMicroseconds())

    def test___eq__(self):
        m1 = Milliseconds(1000)
        m2 = Milliseconds(1000)

        self.assertTrue(m1 == m2)
