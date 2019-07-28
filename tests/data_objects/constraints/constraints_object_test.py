# """
# constraints_object_test.py
#
# Module to test constraints_object.py.
# Author: Tameem Samawi (tsamawi@cra.com)
# """
#
# import unittest
# from cp1.common.exception_class import ConstraintsObjectInitializationException
# from cp1.data_objects.processing.constraints_object import ConstraintsObject
# from cp1.data_objects.processing.channel import Channel
# from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
# from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
# from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
# from cp1.data_objects.mdl.kbps import Kbps
# from cp1.data_objects.mdl.mdl_id import MdlId
# from cp1.data_objects.mdl.frequency import Frequency
# from cp1.data_objects.processing.ta import TA
#
#
# class ConstraintsObjectTest(unittest.TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         cls.goal_throughput_bulk = BandwidthRate(BandwidthTypes.BULK, Kbps(10))
#         cls.goal_throughput_voice = BandwidthRate(BandwidthTypes.VOICE, Kbps(10))
#         cls.goal_throughput_safety = BandwidthRate(BandwidthTypes.SAFETY, Kbps(10))
#         cls.latency = time(microsecond=50000)
#         cls.guard_band = Milliseconds(1000)
#         cls.epoch = Milliseconds(100000)
#         cls.txop_timeout = TxOpTimeout(255)
#
#         channel_frequency = Frequency(4919500000)
#         channel_length = Milliseconds(100)
#         channel_latency = Milliseconds(50)
#         channel_capacity = Kbps(100)
#         cls.channels = [Channel(channel_frequency, channel_length, channel_latency, channel_capacity)]
#
#         ta_id_ = MdlId('TA1')
#         ta_minimum_voice_bandwidth = Kbps(100)
#         ta_minimum_safety_bandwidth = Kbps(75)
#         ta_scaling_factor = 1
#         ta_c = 0.05
#         ta_min_value = 65
#         ta = TA(ta_id_, ta_minimum_voice_bandwidth, ta_minimum_safety_bandwidth, ta_scaling_factor,
#                 ta_c)
#         cls.candidate_tas = [ta]
#
#     def test_valid_constraints_object_init(self):
#         constraints_object = ConstraintsObject(
#                                 self.goal_throughput_bulk,
#                                 self.goal_throughput_voice,
#                                 self.goal_throughput_safety,
#                                 self.latency,
#                                 self.guard_band,
#                                 self.epoch,
#                                 self.txop_timeout,
#                                 self.candidate_tas,
#                                 self.channels)
#         self.assertEqual(self.goal_throughput_bulk,
#                          constraints_object.goal_throughput_bulk)
#         self.assertEqual(self.goal_throughput_voice,
#                          constraints_object.goal_throughput_voice)
#         self.assertEqual(self.goal_throughput_safety,
#                          constraints_object.goal_throughput_safety)
#         self.assertEqual(self.latency,
#                          constraints_object.latency)
#         self.assertEqual(self.guard_band,
#                          constraints_object.guard_band)
#         self.assertEqual(self.epoch,
#                          constraints_object.epoch)
#
#         tas_equal = True
#         for i in range(0, len(self.candidate_tas)):
#             if self.candidate_tas[i] != constraints_object.candidate_tas[i]:
#                 tas_equal = False
#         self.assertTrue(tas_equal)
#
#         channels_equal = True
#         for i in range(0, len(self.channels)):
#             if self.channels[i] != constraints_object.channels[i]:
#                 channels_equal = False
#         self.assertTrue(channels_equal)
#
#     def test___eq__(self):
#         c1 = ConstraintsObject(
#                                 self.goal_throughput_bulk,
#                                 self.goal_throughput_voice,
#                                 self.goal_throughput_safety,
#                                 self.latency,
#                                 self.guard_band,
#                                 self.epoch,
#                                 self.txop_timeout,
#                                 self.candidate_tas,
#                                 self.channels)
#         c2 = ConstraintsObject(
#                                 self.goal_throughput_bulk,
#                                 self.goal_throughput_voice,
#                                 self.goal_throughput_safety,
#                                 self.latency,
#                                 self.guard_band,
#                                 self.epoch,
#                                 self.txop_timeout,
#                                 self.candidate_tas,
#                                 self.channels)
#         self.assertEqual(c1, c2)
#
#     def test_invalid_goal_throughput_bulk(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             1,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             self.txop_timeout,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_goal_throughput_voice(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             1,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             self.txop_timeout,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_goal_throughput_safety(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             1,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             self.txop_timeout,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_guard_band_type(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             1,
#             self.epoch,
#             self.txop_timeout,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_epoch_type(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             1,
#             self.txop_timeout,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_txop_timeout(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             1,
#             self.candidate_tas,
#             self.channels)
#
#     def test_invalid_candidate_tas_type(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             self.txop_timeout,
#             1,
#             self.channels)
#
#     def test_invalid_channels_type(self):
#         self.assertRaises(
#             ConstraintsObjectInitializationException,
#             ConstraintsObject,
#             self.goal_throughput_bulk,
#             self.goal_throughput_voice,
#             self.goal_throughput_safety,
#             self.latency,
#             self.guard_band,
#             self.epoch,
#             self.txop_timeout,
#             self.candidate_tas,
#             1)
