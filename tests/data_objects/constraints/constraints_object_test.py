"""

constraints_object_test.py

Module to test constraints_object.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.common.exception_class import ConstraintsObjectInitializationError
from cp1.data_objects.constraints.constraints_object import ConstraintsObject
from cp1.data_objects.constraints.channel import Channel
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.constraints.ta import TA


class ConstraintsObjectTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        channel_name = MdlId('Channel_1')
        channel_capacity = Kbps(100)
        channel_timeout = TxOpTimeout(255)
        channel_frequency = Frequency(4919500000)
        cls.channel = Channel(channel_name, channel_capacity, channel_timeout, channel_frequency)

        ta_id_ = MdlId('TA1')
        ta_minimum_voice_bandwidth = Kbps(100)
        ta_minimum_safety_bandwidth = Kbps(75)
        ta_scaling_factor = 1
        ta_c = 0.05
        ta_utility_threshold = 65
        ta = TA(ta_id_, ta_minimum_voice_bandwidth, ta_minimum_safety_bandwidth, ta_scaling_factor,
                ta_c, ta_utility_threshold)
        cls.candidate_tas = [ta]

        cls.epoch = Milliseconds(100)
        cls.guard_band = Microseconds(1000)

    # TODO: Overwrite equals methods
    # def test_valid_constraints_object_init(self):
    #     constraints_object = ConstraintsObject(self.guard_band,
    #                             self.epoch,
    #                             self.candidate_tas,
    #                             self.channel)
    #     self.assertEqual(self.guard_band,
    #                      constraints_object.channel)
    #     self.assertEqual(self.epoch,
    #                      constraints_object.epoch)
    #     self.assertEqual(self.candidate_tas,
    #                      constraints_object.candidate_tas)
    #     self.assertEqual(self.channel,
    #                      constraints_object.channel)

    def test_invalid_guard_band_type(self):
        self.assertRaises(
            ConstraintsObjectInitializationError,
            ConstraintsObject,
            1,
            self.epoch,
            self.candidate_tas,
            self.channel)

    def test_invalid_epoch_type(self):
        self.assertRaises(
            ConstraintsObjectInitializationError,
            ConstraintsObject,
            self.guard_band,
            'foo',
            self.candidate_tas,
            self.channel)

    def test_invalid_candidate_tas_type(self):
        self.assertRaises(
            ConstraintsObjectInitializationError,
            ConstraintsObject,
            self.guard_band,
            self.epoch,
            'foo',
            self.channel)

    def test_invalid_channel_type(self):
        self.assertRaises(
            ConstraintsObjectInitializationError,
            ConstraintsObject,
            self.guard_band,
            self.epoch,
            self.candidate_tas,
            'foo')
