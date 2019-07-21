# import unittest
# from cp1.utils.channel_generator import ChannelGenerator
# from cp1.data_objects.mdl.kbps import Kbps
# from cp1.data_objects.mdl.frequency import Frequency
# from cp1.common.exception_class import ChannelGeneratorRangeException
#
#
# class ChannelGeneratorTest(unittest.TestCase):
#     def test_generate_uniformly_correct_amount_of_channels(self):
#         num_channels = 100
#         channel_generator = ChannelGenerator(
#                                 lower_capacity=Kbps(1),
#                                 upper_capacity=Kbps(10000),
#                                 base_frequency_value=Kbps(4919500000),
#                                 base_frequency_incrementation=Kbps(1000))
#         self.assertEqual(len(channel_generator.generate_uniformly(num_channels)), num_channels)
#
#     def test_generates_correct_amount_of_channels(self):
#         num_channels = 100
#         channel_generator = ChannelGenerator()
#         self.assertEqual(len(channel_generator.generate(num_channels)), num_channels)
#
#     # def test_seeding_works(self):
#     #     num_channels = 100
#     #     generator_1 = ChannelGenerator(
#     #                             num_channels=num_channels,
#     #                             lower_length=Milliseconds(101),
#     #                             upper_length=Milliseconds(150),
#     #                             lower_latency=Milliseconds(50),
#     #                             upper_latency=Milliseconds(100),
#     #                             lower_capacity=Kbps(1),
#     #                             upper_capacity=Kbps(10000),
#     #                             seeded=True)
#     #     generator_2 = ChannelGenerator(
#     #                             num_channels=num_channels,
#     #                             lower_length=Milliseconds(101),
#     #                             upper_length=Milliseconds(150),
#     #                             lower_latency=Milliseconds(50),
#     #                             upper_latency=Milliseconds(100),
#     #                             lower_capacity=Kbps(1),
#     #                             upper_capacity=Kbps(10000),
#     #                             seeded=True)
#     #     channels_equal = True
#     #     for i in range(0, len(generator_1.channels)):
#     #         if generator_1.channels[i] != generator_2.channels[i]:
#     #             channels_equal = False
#     #             break
#     #     self.assertTrue(channels_equal)
#     #
#     # def test_validate_lower_length_less_than_lower_latency(self):
#     #     num_channels = 100
#     #     self.assertRaises(ChannelGeneratorRangeException, ChannelGenerator, 100, Milliseconds(49), Milliseconds(150), Milliseconds(50), Milliseconds(100),
#     #                         Kbps(1), Kbps(1000000))
#     #
#     # def test_validate_upper_length_greater_than_upper_latency(self):
#     #     num_channels = 100
#     #     self.assertRaises(ChannelGeneratorRangeException, ChannelGenerator, 100, Milliseconds(50), Milliseconds(99), Milliseconds(50), Milliseconds(100),
#     #                         Kbps(1), Kbps(1000000))
#     #
#     # def test_validate_lower_length_greater_than_upper_length(self):
#     #     num_channels = 100
#     #     self.assertRaises(ChannelGeneratorRangeException, ChannelGenerator, 100, Milliseconds(101), Milliseconds(100), Milliseconds(50), Milliseconds(100),
#     #                         Kbps(1), Kbps(1000000))
#     #
#     # def test_validate_lower_latency_greater_than_upper_latency(self):
#     #     num_channels = 100
#     #     self.assertRaises(ChannelGeneratorRangeException, ChannelGenerator, 100, Milliseconds(120), Milliseconds(150), Milliseconds(101), Milliseconds(100),
#     #                         Kbps(1), Kbps(1000000))
#     #
#     # def test_validate_lower_capacity_greater_than_upper_capacity(self):
#     #     num_channels = 100
#     #     self.assertRaises(ChannelGeneratorRangeException, ChannelGenerator, 100, Milliseconds(50), Milliseconds(99), Milliseconds(101), Milliseconds(100),
#     #                         Kbps(100), Kbps(1))
