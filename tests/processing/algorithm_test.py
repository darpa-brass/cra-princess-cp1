# import unittest
# from cp1.processing.algorithm import Algorithm
# from cp1.processing.algorithm_type import AlgorithmType
# from cp1.data_objects.processing.constraints_object import ConstraintsObject
# from cp1.data_objects.processing.ta import TA
# from cp1.data_objects.processing.channel import Channel
# from cp1.data_objects.mdl.kbps import Kbps
# from cp1.data_objects.mdl.mdl_id import MdlId
# from cp1.data_objects.mdl.frequency import Frequency
# from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
# from cp1.data_objects.mdl.txop import TxOp
# from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
# from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
#
#
# class AlgorithmTest(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.ta_1 = TA(id_=MdlId('TA1'), minimum_voice_bandwidth=Kbps(25),
#                       minimum_safety_bandwidth=Kbps(25), scaling_factor=1,
#                       c=0.005)
#         cls.ta_2 = TA(id_=MdlId('TA2'), minimum_voice_bandwidth=Kbps(25),
#                       minimum_safety_bandwidth=Kbps(100), scaling_factor=1,
#                       c=0.007)
#         cls.ta_3 = TA(id_=MdlId('TA3'), minimum_voice_bandwidth=Kbps(15),
#                       minimum_safety_bandwidth=Kbps(15), scaling_factor=1,
#                       c=0.005)
#         cls.ta_4 = TA(id_=MdlId('TA4'), minimum_voice_bandwidth=Kbps(10),
#                       minimum_safety_bandwidth=Kbps(5), scaling_factor=1,
#                       c=0.5)
#         cls.ta_5 = TA(id_=MdlId('TA5'), minimum_voice_bandwidth=Kbps(10),
#                       minimum_safety_bandwidth=Kbps(5), scaling_factor=1,
#                       c=0.5)
#         cls.channels = []
#         channel_1 = Channel(frequency=Frequency(4919500000), latency=Milliseconds(50000),
#                             length=Milliseconds(100000))
#         cls.channels.append(channel_1)
#
#         cls.constraints_object = ConstraintsObject(goal_throughput_bulk=BandwidthRate(rate=Kbps(150), type_=BandwidthTypes.BULK),
#                                             goal_throughput_voice=BandwidthRate(rate=Kbps(100), type_=BandwidthTypes.VOICE),
#                                             goal_throughput_safety=BandwidthRate(rate=Kbps(100), type_=BandwidthTypes.SAFETY),
#                                             candidate_tas=[cls.ta_1,
#                                                            cls.ta_2,
#                                                           cls.ta_3,
#                                                           cls.ta_4,
#                                                           cls.ta_5],
#                                            latency=Milliseconds(50),
#                                            guard_band=Milliseconds(1),
#                                            epoch=Milliseconds(100),
#                                            channels=cls.channels,
#                                            txop_timeout=TxOpTimeout(255))
#
#     def test_valid_schedule(self):
#         algorithm = Algorithm(constraints_object=self.constraints_object, algorithm_type=AlgorithmType.GREEDY)
#         new_schedule = algorithm.optimize()
#
#         self.assertEqual()
#
#     def test_only_one_ta_fits(self):
#         constraints_object = ConstraintsObject()
#
#     #TODO
#     def test_all_tas_fit(self):
#         return
#
#     #TODO
#     def test_tas_require_0_bandwidth(self):
#         return
#
#     #TODO
#     def test_no_tas_fit(self):
#         return
#
#     #TODO
#     def test_latency_not_factor_of_epoch(self):
#         return
#
#     #TODO
#     def test_latency_equals_epoch(self):
#         return
#
#     #TODO
#     def test_epoch_less_than_latency(self):
#         return
#
#     #TODO
#     def test_guard_band_of_0(self):
#         return
#
#     #TODO
#     def test_guard_band_of_10(self):
#         return
