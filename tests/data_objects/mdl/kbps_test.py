"""
kbps_test.py

Module to test kbps.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.kbps import Kbps
from cp1.common.exception_class import KbpsInitializationException


class KbpsTest(unittest.TestCase):
    def test_valid_init(self):
        value = 10000
        kbps = Kbps(value)
        self.assertEqual(value, kbps.value)

    def test_invalid_init_value(self):
        self.assertRaises(
            KbpsInitializationException,
            Kbps,
            -1)

    def test_invalid_init_type(self):
        self.assertRaises(
            KbpsInitializationException,
            Kbps,
            'Foo')

    def test_to_bits_per_second(self):
        kbps = Kbps(100)
        self.assertEqual(100000, kbps.to_bits_per_second())

    def test__eq__(self):
        kbps1 = Kbps(100)
        kbps2 = Kbps(100)
        self.assertEqual(kbps1, kbps2)
