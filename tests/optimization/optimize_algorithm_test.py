# from optimizer import Optimizer
# import unittest
# import sys
# sys.path.insert(0, '../../src/scenarios')
#
#
# class OptimizaAlgorithmTest(unittest.TestCase):
#     def setUp(self):
#         self.optimizer = Optimizer
#
#     def test_optimize(self):
#         timeout = 255
#         frequency = 4919500000
#
#         txop1 = TxOp(start=0, stop=11500, timeout=timeout, frequency=frequency)
#         txop2 = TxOp(
#             start=12500,
#             stop=24000,
#             timeout=timeout,
#             frequency=frequency)
#         txop3 = TxOp(
#             start=25000,
#             stop=48000,
#             timeout=timeout,
#             frequency=frequency)
#         txop4 = TxOp(
#             start=49000,
#             stop=74000,
#             timeout=timeout,
#             frequency=frequency)
#         txop5 = TxOp(
#             start=75000,
#             stop=86500,
#             timeout=timeout,
#             frequency=frequency)
#         txop6 = TxOp(
#             start=87500,
#             stop=99000,
#             timeout=timeout,
#             frequency=frequency)
#
#         new_schedule = [txop1, txop2, txop3, txop4, txop5, txop6]
#
#         voice_bandwidth_rate = BandwidthRate("GR1_to_TA1_SLP_1_20", 75000,
#                                              "TA1_to_GndGrp1_SLP_1_20", 7500)
#         safety_bandwidth_rate = BandwidthRate(
#             "GR1_to_TA1_SLP_1_301", 0, "TA1_to_GndGrp1_SLP_1_301", 542000)
#         bulk_bandwidth_rate = BandwidthRate("GR1_to_TA1_SLP_1_40", 9244000,
#                                             "TA1_to_GndGrp1_SLP_1_40", 0)
#         rfnm_bandwidth_rate = BandwidthRate("GR1_to_TA1_SLP_1_10", 32000,
#                                             "TA1_to_GndGrp1_SLP_1_10", 32000)
#
#         bandwidth_rates = {
#             'voice': voice_bandwidth_rate,
#             'safety': safety_bandwidth_rate,
#             'bulk': bulk_bandwidth_rate,
#             'rfnm': rfnm_bandwidth_rate}
#
#         expected = OptimizationResult(new_schedule, bandwidth_rates)
#         actual = self.optimizer.optimize
#
#         self.assertTrue(expected, actual)
