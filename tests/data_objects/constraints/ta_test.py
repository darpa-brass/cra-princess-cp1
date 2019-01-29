
"""

ta_test.py

Module to test ta.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.constraints.ta import TA
from cp1.common.exception_class import TAInitializationError
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId


class MillisecondsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.id_ = MdlId('TA1')
        cls.minimum_voice_bandwidth = Kbps(100)
        cls.minimum_safety_bandwidth = Kbps(75)
        cls.scaling_factor = 1
        cls.c = 0.05
        cls.utility_threshold = 65

    def test_valid_TA(self):
        ta = TA(self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                self.scaling_factor, self.c, self.utility_threshold)
        self.assertEqual(self.id_.value, ta.id_.value)
        self.assertEqual(self.minimum_voice_bandwidth, ta.minimum_voice_bandwidth)
        self.assertEqual(self.minimum_safety_bandwidth, ta.minimum_safety_bandwidth)
        self.assertEqual(self.scaling_factor, ta.scaling_factor)
        self.assertEqual(self.c, ta.c)
        self.assertEqual(self.utility_threshold, ta.utility_threshold)

    def test_invalid_TA_id(self):
        self.assertRaises(TAInitializationError, TA, 'foo', self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          self.scaling_factor, self.c, self.utility_threshold)

    def test_invalid_TA_minimum_voice_bandwidth(self):
        self.assertRaises(TAInitializationError, TA, self.id_, 10, self.minimum_safety_bandwidth,
                          self.scaling_factor, self.c, self.utility_threshold)

    def test_invalid_TA_minimum_safety_bandwidth(self):
        self.assertRaises(TAInitializationError, TA, self.id_, self.minimum_voice_bandwidth, 10,
                          self.scaling_factor, self.c, self.utility_threshold)

    def test_invalid_TA_scaling_factor(self):
        self.assertRaises(TAInitializationError, TA, self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          'foo', self.c, self.utility_threshold)

    def test_invalid_TA_c(self):
        self.assertRaises(TAInitializationError, TA, self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          self.scaling_factor, 'foo', self.utility_threshold)

    def test_invalid_TA_utility_threshold(self):
        self.assertRaises(TAInitializationError, TA, self.id_, self.minimum_voice_bandwidth, self.minimum_safety_bandwidth,
                          self.scaling_factor, self.c, 'foo')