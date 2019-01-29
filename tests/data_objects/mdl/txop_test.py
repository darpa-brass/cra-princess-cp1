"""

txop_test.py

Module to test txop.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.txop import TxOp
from cp1.common.exception_class import TxOpInitializationError


class TxOpTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_usec = Microseconds(0)
        cls.stop_usec = Microseconds(10500)
        cls.center_frequency_hz = Frequency(1495000)
        cls.txop_timeout = TxOpTimeout(255)

    def test_valid_txop_init(self):
        txop = TxOp(
            self.start_usec,
            self.stop_usec,
            self.center_frequency_hz,
            self.txop_timeout)

        self.assertEqual(self.start_usec, txop.start_usec)
        self.assertEqual(self.stop_usec, txop.stop_usec)
        self.assertEqual(
            self.center_frequency_hz,
            txop.center_frequency_hz)
        self.assertEqual(
            self.txop_timeout,
            txop.txop_timeout)

    def test_invalid_start_usec_type(self):
        self.assertRaises(
            TxOpInitializationError,
            TxOp,
            'foo',
            self.stop_usec,
            self.center_frequency_hz,
            self.txop_timeout)

    def test_invalid_stop_usec_type(self):
        self.assertRaises(
            TxOpInitializationError,
            TxOp,
            self.start_usec,
            'foo',
            self.center_frequency_hz,
            self.txop_timeout)

    def test_invalid_start_usec_after_stop(self):
        self.assertRaises(
            TxOpInitializationError,
            TxOp,
            Microseconds(300),
            Microseconds(200),
            self.center_frequency_hz,
            self.txop_timeout)

    def test_invalid_center_frequency_type(self):
        self.assertRaises(
            TxOpInitializationError,
            TxOp,
            self.start_usec,
            self.stop_usec,
            'foo',
            self.txop_timeout)

    def test_invalid_timeout_type(self):
        self.assertRaises(
            TxOpInitializationError,
            TxOp,
            self.start_usec,
            self.stop_usec,
            self.center_frequency_hz,
            'foo'
        )

