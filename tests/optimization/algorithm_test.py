import unittest
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.txop import TxOp


class AlgorithmTest:
    def test_optimize(self):
        start_usec_1 = Microseconds(0)
        stop_usec_1 = Microseconds(10000)
        center_frequency_hz_1 = Frequency(49196000)
        txop_timeout_1 = TxOpTimeout(255)
        txop_1 = TxOp(start_usec_1, stop_usec_1, center_frequency_hz_1, txop_timeout_1)

        start_usec_2 = Microseconds(11000)
        stop_usec_2 = Microseconds(21000)
        center_frequency_hz_2 = Frequency(49196000)
        txop_timeout_2 = TxOpTimeout(255)
        txop_2 = TxOp(start_usec_2, stop_usec_2, center_frequency_hz_2, txop_timeout_2)

        start_usec_3 = Microseconds(22000)
        stop_usec_3 = Microseconds(32000)
        center_frequency_hz_3 = Frequency(49196000)
        txop_timeout_3 = TxOpTimeout(255)
        txop_3 = TxOp(start_usec_3, stop_usec_3, center_frequency_hz_3, txop_timeout_3)

        start_usec_4 = Microseconds(33000)
        stop_usec_4 = Microseconds(43000)
        center_frequency_hz_4 = Frequency(49196000)
        txop_timeout_4 = TxOpTimeout(255)
        txop_4 = TxOp(start_usec_4, stop_usec_4, center_frequency_hz_4, txop_timeout_4)

        start_usec_5 = Microseconds(44000)
        stop_usec_5 = Microseconds(54000)
        center_frequency_hz_5 = Frequency(49196000)
        txop_timeout_5 = TxOpTimeout(255)
        txop_5 = TxOp(start_usec_5, stop_usec_5, center_frequency_hz_5, txop_timeout_5)

        start_usec_6 = Microseconds(55000)
        stop_usec_6 = Microseconds(65000)
        center_frequency_hz_6 = Frequency(49196000)
        txop_timeout_6 = TxOpTimeout(255)
        txop_6 = TxOp(start_usec_6, stop_usec_6, center_frequency_hz_6, txop_timeout_6)

        start_usec_7 = Microseconds(66000)
        stop_usec_7 = Microseconds(76000)
        center_frequency_hz_7 = Frequency(49196000)
        txop_timeout_7 = TxOpTimeout(255)
        txop_7 = TxOp(start_usec_7, stop_usec_7, center_frequency_hz_7, txop_timeout_7)

        start_usec_8 = Microseconds(77000)
        stop_usec_8 = Microseconds(88000)
        center_frequency_hz_8 = Frequency(49196000)
        txop_timeout_8 = TxOpTimeout(255)
        txop_8 = TxOp(start_usec_8, stop_usec_8, center_frequency_hz_8, txop_timeout_8)

        start_usec_9 = Microseconds(89000)
        stop_usec_9 = Microseconds(99000)
        center_frequency_hz_9 = Frequency(49196000)
        txop_timeout_9 = TxOpTimeout(255)
        txop_9 = TxOp(start_usec_9, stop_usec_9, center_frequency_hz_9, txop_timeout_9)

