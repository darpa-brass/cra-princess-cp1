"""
bandwidth_types_test.py

Module to test bandwidth_types.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes


class BandwidthTypesTest(unittest.TestCase):
    def test_voice(self):
        self.assertTrue('VOICE' in BandwidthTypes.__members__)

    def test_safety(self):
        self.assertTrue('SAFETY' in BandwidthTypes.__members__)

    def test_rfnm(self):
        self.assertTrue('RFNM' in BandwidthTypes.__members__)

    def test_bulk(self):
        self.assertTrue('BULK' in BandwidthTypes.__members__)
