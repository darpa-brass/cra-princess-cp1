"""
ta_test.py

Module to test ta.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.processing.ta import TA
from cp1.common.exception_class import TAInitializationException
from cp1.common.exception_class import ComputeValueException
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId


class TATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MdlId.clear()
        cls.id_ = MdlId('TA1')
        cls.minimum_voice_bandwidth = Kbps(100)
        cls.minimum_safety_bandwidth = Kbps(75)
        cls.scaling_factor = 1
        cls.c = 0.05

    def test_valid_ta_init(self):
        ta = TA(self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                self.scaling_factor, self.c)
        self.assertEqual(self.id, ta.id)
        self.assertEqual(self.minimum_voice_bandwidth, ta.minimum_voice_bandwidth)
        self.assertEqual(self.minimum_safety_bandwidth, ta.minimum_safety_bandwidth)
        self.assertEqual(self.scaling_factor, ta.scaling_factor)
        self.assertEqual(self.c, ta.c)
        self.assertEqual(ta.compute_value(ta.total_minimum_bandwidth.value), ta.min_value)

    def test_compute_value_caps_at_2000(self):
        ta = TA(self.id_, Kbps(2000), Kbps(2000), self.scaling_factor, self.c)
        ta2 = TA(self.id_, Kbps(2000), Kbps(0), self.scaling_factor, self.c)
        self.assertEqual(ta.min_value, ta2.min_value)
        self.assertEqual(100, ta.min_value)

    def test_compute_value_below_minimum_bandwidth(self):
        ta = TA(self.id_, Kbps(200), Kbps(0), self.scaling_factor, self.c)
        self.assertEqual(0, ta.compute_value(1))

    def test_compute_value_negative(self):
        ta = TA(self.id_, Kbps(200), Kbps(0), self.scaling_factor, self.c)
        self.assertRaises(ComputeValueException, ta.compute_value, -1)

    def test_compute_value_at_minimum(self):
        ta = TA(self.id_, Kbps(200), Kbps(0), self.scaling_factor, self.c)
        value = ta.compute_value(200)
        self.assertTrue(value >= 99.995 and value <= 99.996)

    def test_compute_value_at_500_05_0002(self):
        ta = TA(self.id_, Kbps(500), Kbps(0), 0.5, 0.002)
        self.assertTrue(ta.min_value >= 31.606 and ta.min_value <= 31.607)

    def test_compute_value_at_750_01_0004(self):
        ta = TA(self.id_, Kbps(750), Kbps(0), 0.1, 0.004)
        self.assertTrue(ta.min_value >= 9.502 and ta.min_value <= 9.503)

    def test_compute_value_at_1000_025_0007(self):
        ta = TA(self.id_, Kbps(1000), Kbps(0), 0.25, 0.007)
        self.assertTrue(ta.min_value >= 24.977 and ta.min_value <= 24.978)

    def test_compute_value_1250_06_0009(self):
        ta = TA(self.id_, Kbps(500), Kbps(750), 0.6, 0.009)
        self.assertTrue(ta.min_value >= 59.999 and ta.min_value <= 60)

    def test_compute_value_1500_08_0001(self):
        ta = TA(self.id_, Kbps(1500), Kbps(0), 0.8, 0.001)
        self.assertTrue(ta.min_value >= 62.149 and ta.min_value <= 62.150)

    def test_compute_value_1750_03_001(self):
        ta = TA(self.id_, Kbps(1500), Kbps(250), 0.3, 0.001)
        self.assertTrue(ta.min_value >= 24.786 and ta.min_value <= 24.787)

    def test___eq__(self):
        ta1 = TA(self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                self.scaling_factor, self.c)
        ta2 = TA(self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                self.scaling_factor, self.c)
        self.assertEqual(ta1, ta2)

    def test_invalid_TA_id(self):
        self.assertRaises(TAInitializationException, TA, 'foo', self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          self.scaling_factor, self.c)

    def test_invalid_TA_minimum_voice_bandwidth(self):
        self.assertRaises(TAInitializationException, TA, self.id_, 10, self.minimum_safety_bandwidth,
                          self.scaling_factor, self.c)

    def test_invalid_TA_minimum_safety_bandwidth(self):
        self.assertRaises(TAInitializationException, TA, self.id_, self.minimum_voice_bandwidth, 10,
                          self.scaling_factor, self.c)

    def test_invalid_TA_scaling_factor(self):
        self.assertRaises(TAInitializationException, TA, self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          'foo', self.c)

    def test_invalid_TA_c(self):
        self.assertRaises(TAInitializationException, TA, self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          self.scaling_factor, 'foo')
