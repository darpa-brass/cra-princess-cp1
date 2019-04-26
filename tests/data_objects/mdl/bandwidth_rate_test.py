"""
bandwidth_rate_test.py

Module to test bandwidth_rate.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.kbps import Kbps
from cp1.common.exception_class import BandwidthRateInitializationException


class BandwidthRateTest(unittest.TestCase):
    def test_bandwidth_rate_init(self):
        type_ = BandwidthTypes.VOICE
        rate = Kbps(100)

        bandwidth_rate = BandwidthRate(type_, rate)
        self.assertEqual(type_, bandwidth_rate.type_)
        self.assertEqual(rate, bandwidth_rate.rate)

    def test_bandwidth_rate_invalid_type(self):
        self.assertRaises(BandwidthRateInitializationException, BandwidthRate,
                          'foo', Kbps(100))

    def test_bandwidth_rate_invalid_rate(self):
        self.assertRaises(BandwidthRateInitializationException, BandwidthRate,
                          BandwidthTypes.VOICE, 'foo')

    def test___eq__(self):
        b1 = BandwidthRate(BandwidthTypes.VOICE, Kbps(100))
        b2 = BandwidthRate(BandwidthTypes.VOICE, Kbps(100))
        self.assertEqual(b1, b2)
