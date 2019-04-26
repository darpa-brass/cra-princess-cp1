"""
exception_class_test.py

Module to test exception_class.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.common.exception_class import *


class ExceptionClassTest(unittest.TestCase):
    def test_node_not_found_exception(self):
        x = NodeNotFoundException('Test')
        self.assertIsInstance(x, NodeNotFoundException)

    def test_tas_not_found_exception(self):
        x = TAsNotFoundException('Test')
        self.assertIsInstance(x, TAsNotFoundException)

    def test_algorithm_initialization_exception(self):
        x = AlgorithmInitializationException('Test')
        self.assertIsInstance(x, AlgorithmInitializationException)

    def test_process_bandwidth_initialization_exception(self):
        x = ProcessBandwidthInitializationException('Test')
        self.assertIsInstance(x, ProcessBandwidthInitializationException)

    def test_bandwidth_rate_initialization_exception(self):
        x = BandwidthRateInitializationException('Test')
        self.assertIsInstance(x, BandwidthRateInitializationException)

    def test_frequency_initialization_exception(self):
        x = FrequencyInitializationException('Test')
        self.assertIsInstance(x, FrequencyInitializationException)

    def test_txop_timeout_initialization_exception(self):
        x = TxOpTimeoutInitializationException('Test')
        self.assertIsInstance(x, TxOpTimeoutInitializationException)

    def test_kbps_initialization_exception(self):
        x = KbpsInitializationException('Test')
        self.assertIsInstance(x, KbpsInitializationException)

    def test_mdl_id_initialization_exception(self):
        x = MdlIdInitializationException('Test')
        self.assertIsInstance(x, MdlIdInitializationException)

    def test_milliseconds_initialization_exception(self):
        x = MillisecondsInitializationException('Test')
        self.assertIsInstance(x, MillisecondsInitializationException)

    def test_microseconds_initialization_exception(self):
        x = MicrosecondsInitializationException('Test')
        self.assertIsInstance(x, MicrosecondsInitializationException)

    def test_ta_generator_initialization_exception(self):
        x = TAGeneratorInitializationException('Test')
        self.assertIsInstance(x, TAGeneratorInitializationException)

    def test_ta_generator_range_exception(self):
        x = TAGeneratorRangeException('Test')
        self.assertIsInstance(x, TAGeneratorRangeException)

    def test_txop_initialization_exception(self):
        x = TxOpInitializationException('Test')
        self.assertIsInstance(x, TxOpInitializationException)

    def test_optimization_result_initialization_exception(self):
        x = OptimizationResultInitializationException('Test')
        self.assertIsInstance(x, OptimizationResultInitializationException)

    def test_schedule_initialization_exception(self):
        x = ScheduleInitializationException('Test')
        self.assertIsInstance(x, ScheduleInitializationException)

    def test_schedule_add_exception(self):
        x = ScheduleAddException('Test')
        self.assertIsInstance(x, ScheduleAddException)

    def test_invalid_algorithm_exception(self):
        x = InvalidAlgorithmException('Test')
        self.assertIsInstance(x, InvalidAlgorithmException)

    def test_store_result_initialization_exception(self):
        x = StoreResultInitializationException('Test')
        self.assertIsInstance(x, StoreResultInitializationException)

    def test_system_wide_constraints_not_found_exception(self):
        x = SystemWideConstraintsNotFoundException('Test')
        self.assertIsInstance(x, SystemWideConstraintsNotFoundException)

    def test_constraints_not_found_exception(self):
        x = ConstraintsNotFoundException('Test')
        self.assertIsInstance(x, ConstraintsNotFoundException)

    def test_ta_initialization_exception(self):
        x = TAInitializationException('Test')
        self.assertIsInstance(x, TAInitializationException)

    def test_channel_initialization_exception(self):
        x = ChannelInitializationException('Test')
        self.assertIsInstance(x, ChannelInitializationException)

    def test_constraints_object_initialization_exception(self):
        x = ConstraintsObjectInitializationException('Test')
        self.assertIsInstance(x, ConstraintsObjectInitializationException)

    def test_invalid_schedule_exception(self):
        x = InvalidScheduleException('Test')
        self.assertIsInstance(x, InvalidScheduleException)

    def test_compute_value_exception(self):
        x = ComputeValueException('Test')
        self.assertIsInstance(x, ComputeValueException)
