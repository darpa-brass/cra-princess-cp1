"""

kbps_test.py

Module to test kbps.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.mdl.kbps import Kbps
from cp1.common.exception_class import KbpsInitializationError


class KbpsTest(unittest.TestCase):
    def test_valid_millisecond(self):
        value = 10000
        kbps = Kbps(value)
        self.assertEqual(value, kbps.value)

    def test_invalid_millisecond_value_negative(self):
        self.assertRaises(
            KbpsInitializationError,
            Kbps,
            -1000)

    def test_invalid_millisecond_value_type(self):
        self.assertRaises(
            KbpsInitializationError,
            Kbps,
            'Foo')
