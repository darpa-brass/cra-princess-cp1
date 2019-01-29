"""

channel_test.py

Module to test channel.py.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import unittest
from cp1.data_objects.constraints.channel import Channel
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.timeout import Timeout
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.common.exception_class import ChannelInitializationError


class ChannelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.valid_channel_name = MdlId('Channel_1')
        cls.valid_channel_capacity = Kbps(100)
        cls.valid_channel_timeout = Timeout(255)
        cls.valid_channel_frequency = Frequency(4919500000)

    def test_valid_channel_init(self):
        valid_channel = Channel(self.valid_channel_name,
                                self.valid_channel_capacity,
                                self.valid_channel_timeout,
                                self.valid_channel_frequency)
        self.assertEqual(self.valid_channel_name,
                         valid_channel.name)
        self.assertEqual(self.valid_channel_capacity,
                         valid_channel.capacity)
        self.assertEqual(self.valid_channel_timeout,
                         valid_channel.timeout)
        self.assertEqual(self.valid_channel_frequency,
                         valid_channel.frequency)

    def test_invalid_channel_name_type(self):
        self.assertRaises(
            ChannelInitializationError,
            Channel,
            1,
            self.valid_channel_capacity,
            self.valid_channel_timeout,
            self.valid_channel_frequency)

    def test_invalid_channel_capacity_type(self):
        self.assertRaises(
            ChannelInitializationError,
            Channel,
            self.valid_channel_name,
            'foo',
            self.valid_channel_timeout,
            self.valid_channel_frequency)

    def test_invalid_channel_timeout_type(self):
        self.assertRaises(ChannelInitializationError, Channel,
                          self.valid_channel_name, self.valid_channel_capacity,
                          1, self.valid_channel_frequency)

    def test_invalid_channel_frequency_type(self):
        self.assertRaises(ChannelInitializationError, Channel,
                          self.valid_channel_name, self.valid_channel_capacity,
                          self.valid_channel_timeout, 'foo')
