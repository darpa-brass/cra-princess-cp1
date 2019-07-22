"""
schedule_test.py

Module to test the schedule.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import unittest
from cp1.common.exception_class import ScheduleInitializationException
from cp1.common.exception_class import ScheduleAddException
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout


class ScheduleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        start_usec_1 = Microseconds(0)
        stop_usec_1 = Microseconds(10500)
        center_frequency_hz_1 = Frequency(14500)
        txop_timeout_1 = TxOpTimeout(255)
        cls.txop_1 = TxOp(
            start_usec_1,
            stop_usec_1,
            center_frequency_hz_1,
            txop_timeout_1)

        start_usec_2 = Microseconds(11500)
        stop_usec_2 = Microseconds(25000)
        center_frequency_hz_2 = Frequency(14500)
        txop_timeout_2 = TxOpTimeout(255)
        cls.txop_2 = TxOp(
            start_usec_2,
            stop_usec_2,
            center_frequency_hz_2,
            txop_timeout_2)

        start_usec_3 = Microseconds(26000)
        stop_usec_3 = Microseconds(37000)
        center_frequency_hz_3 = Frequency(14500)
        txop_timeout_3 = TxOpTimeout(255)
        cls.txop_3 = TxOp(
            start_usec_3,
            stop_usec_3,
            center_frequency_hz_3,
            txop_timeout_3)

        cls.new_schedule = [cls.txop_1, cls.txop_2, cls.txop_3]
        cls.radio_link_key = 'TA_to_Gnd'

    def setUp(self):
        epoch = Milliseconds(100)
        guard_band = Milliseconds(1)
        self.schedule = Schedule(epoch, guard_band)

    def test_valid_schedule_init(self):
        self.assertTrue(len(self.schedule.schedule) == 0)

    def test_valid_add(self):
        self.schedule.add(self.radio_link_key, self.txop_1)

        txop_list = self.schedule.schedule[self.radio_link_key]
        self.assertEqual(txop_list[0], self.txop_1)

    def test_invalid_add_radio_link_key(self):
        self.assertRaises(ScheduleAddException, self.schedule.add, 100,
                          self.txop_1)

    def test_invalid_add_txop_type(self):
        self.assertRaises(
            ScheduleAddException,
            self.schedule.add,
            self.radio_link_key,
            'foo')

    def test_invalid_schedule_init_epoch(self):
        self.assertRaises(
            ScheduleInitializationException,
            Schedule,
            'foo',
            Milliseconds(1))

    def test_invalid_schedule_init_guard_band(self):
        self.assertRaises(
            ScheduleInitializationException,
            Schedule,
            Milliseconds(10),
            'foo')

    def test___eq__(self):
        s1 = Schedule(Milliseconds(0), Milliseconds(0))
        s1.add('Gnd_to_TA', self.txop_1)

        s2 = Schedule(Milliseconds(0), Milliseconds(0))
        s2.add('Gnd_to_TA', self.txop_1)

        self.assertTrue(s1 == s2)

    def test___eq___incorrect_key(self):
        s1 = Schedule(Milliseconds(0), Milliseconds(0))
        s1.add('TA_to_Gnd', self.txop_1)

        s2 = Schedule(Milliseconds(0), Milliseconds(0))
        s2.add('Gnd_to_TA', self.txop_1)

        self.assertTrue(s1 != s2)

    def test___eq___incorrect_value(self):
        s1 = Schedule(Milliseconds(0), Milliseconds(0))
        s1.add('Gnd_to_TA', self.txop_2)

        s2 = Schedule(Milliseconds(0), Milliseconds(0))
        s2.add('Gnd_to_TA', self.txop_1)

        self.assertTrue(s1 != s2)

    def test___eq___empty_schedule(self):
        s1 = Schedule(Milliseconds(0), Milliseconds(0))
        s2 = Schedule(Milliseconds(0), Milliseconds(0))

        self.assertTrue(s1 == s2)
