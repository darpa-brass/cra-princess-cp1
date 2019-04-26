"""
channel_test.py

Module to test channel.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.common.exception_class import ChannelInitializationException


class ChannelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_channel_frequency = Frequency(4919500000)
        cls.valid_channel_length = Milliseconds(100)
        cls.valid_channel_latency = Milliseconds(50)
        cls.valid_channel_capacity = Kbps(100000)

        cls.valid_channel = Channel(
                            cls.valid_channel_frequency,
                            cls.valid_channel_length,
                            cls.valid_channel_latency,
                            cls.valid_channel_capacity)

    def test_valid_channel_init(self):
        self.assertEqual(self.valid_channel_frequency.value,
                         self.valid_channel.frequency.value)
        self.assertEqual(self.valid_channel_length.value,
                         self.valid_channel.length.value)
        self.assertEqual(self.valid_channel_latency.value,
                         self.valid_channel.latency.value)
        self.assertEqual(self.valid_channel_capacity.value,
                         self.valid_channel.capacity.value)

    def test___eq__(self):
        channel_2 = Channel(
                    self.valid_channel_frequency,
                    self.valid_channel_length,
                    self.valid_channel_latency,
                    self.valid_channel_capacity)

        self.assertEqual(self.valid_channel, channel_2)

    def test_invalid_channel_frequency_type(self):
        self.assertRaises(
            ChannelInitializationException,
            Channel,
            'foo',
            self.valid_channel_length,
            self.valid_channel_latency,
            self.valid_channel_capacity)

    def test_invalid_channel_length_type(self):
        self.assertRaises(
            ChannelInitializationException,
            Channel,
            self.valid_channel_frequency,
            'foo',
            self.valid_channel_latency,
            self.valid_channel_capacity)

    def test_invalid_channel_latency_type(self):
        self.assertRaises(
            ChannelInitializationException,
            Channel,
            self.valid_channel_frequency,
            self.valid_channel_length,
            'foo',
            self.valid_channel_capacity)

    def test_invalid_channel_capacity_type(self):
        self.assertRaises(
            ChannelInitializationException,
            Channel,
            self.valid_channel_frequency,
            self.valid_channel_length,
            self.valid_channel_latency,
            'foo')

    def test_num_partitions(self):
        self.assertEqual(2, self.valid_channel.num_partitions)

    def test_value(self):
        self.assertEqual(0, self.valid_channel.value)

    def test_first_available_time(self):
        self.assertEqual(0, self.valid_channel.first_available_time)

    def test_partition_length(self):
        self.assertEqual(50, self.valid_channel.partition_length)
