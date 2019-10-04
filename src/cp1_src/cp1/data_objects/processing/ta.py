"""ta.py

Data object representing a TA.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
from cp1.utils.decorators.timedelta import timedelta
from cp1.common.exception_class import ComputeValueException
from cp1.common.exception_class import ComputeBandwidthException
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.constants.constants import *
from cp1.common.logger import Logger

logger = Logger().logger

class TA:
    def __init__(
            self,
            id_,
            minimum_voice_bandwidth,
            minimum_safety_bandwidth,
            latency,
            scaling_factor,
            c,
            eligible_frequencies,
            bandwidth=Kbps(0),
            channel=None,
            value=0):
        """Constructor

        :param str id_: The ID of the TA.
        :param Kbps minimum_voice_bandwidth: The minimum required voice bandwidth to get this TA in the air
        :param Kbps minimum_safety_bandwidth: The minimum required safety bandwidth to get this TA in the air
        :param timedelta latency: The maximum delay between radio transmissions
        :param int scaling_factor: The amount by which to scale the overall value by onc.
        :param int c: The coefficient of a sample value function. For now it's set to 1 because there is no real value
                  function.
        :param List[Channel] eligible_frequencies: The list of channels communication is permissible over.
        :param Kbps bandwidth: The amount of bandwidth assigned to this TA
        :param Channel channel: The channel this TA has been assigned to communicate on
        :param timedelta channel: The channel this TA has been assigned to communicate on
        :param int value: The amount of value this TA provides at a some bandwidth
        """
        self.id_ = id_
        self.minimum_voice_bandwidth = minimum_voice_bandwidth
        self.minimum_safety_bandwidth = minimum_safety_bandwidth
        self.latency = latency
        self.scaling_factor = float(scaling_factor)
        self.c = float(c)
        self.eligible_frequencies = eligible_frequencies
        self.bandwidth = bandwidth
        self.channel = channel
        self.value = value
        self.total_minimum_bandwidth = Kbps(
            minimum_voice_bandwidth.value + minimum_safety_bandwidth.value)
        self.min_value = self.compute_value_at_bandwidth(self.total_minimum_bandwidth)
        self.max_value = self.compute_value_at_bandwidth(MAX_BANDWIDTH)

    def compute_bandwidth_at_value(self, x):
        """Computes bandwidth required to achieve a certain value.

        :param int x: The desired amount of value this TA should provide.
        :returns int bandwidth: The amount of bandwidth this TA will require to provide the specified value.
        """
        if x < 0:
            raise ComputeBandwidthException(
                'Value must be greater than 0: {0}'.format(x),
                'TA.compute_bandwidth')
        elif x < self.min_value:
            return 0
        elif x < self.max_value:
            return -math.log(1 - (x/(100*self.scaling_factor))) / self.c
        else:
            return MAX_BANDWIDTH.value

    def compute_value_at_bandwidth(self, x):
        """Computes value provided at a certain bandwidth.

        :param Kbps x: The amount of bandwidth allocated to this TA.
        :returns int value: The value this TA provides at that bandwidth.
        """
        x = x.value

        if x < 0:
            raise ComputeValueException(
                'Bandwidth must be greater than 0: {0}'.format(x),
                'TA.compute_value')
        elif x < self.total_minimum_bandwidth.value:
            return 0.0
        elif x < MAX_BANDWIDTH.value:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * x)))
        else:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * MAX_BANDWIDTH.value)))

    def compute_communication_length(self, channel_capacity, latency, guard_band=timedelta(microseconds=0)):
        """Returns the amount of bandwidth required to allocate to this TA within the min_interval.
        The output will be a multiple of min_interval + 2 * guard_band.

        :param Kbps channel_capacity: The capacity of the channel
        :param timedelta guard_band: The guard_band requirement
        :returns timedelta communication_length: The amount of time this TA must communicate for to meet it's bandwidth requirement
        """
        two_way_min_interval = 2 * MDL_MIN_INTERVAL
        communication_length = ((self.bandwidth.value / channel_capacity.value) * latency.get_microseconds()) + (2 * guard_band.get_microseconds())

        # Round value to return within the specified MIN_INTERVAL
        dist_from_interval = two_way_min_interval.get_microseconds() -  ((communication_length - 2 * guard_band.get_microseconds()) %  (two_way_min_interval.get_microseconds()))
        communication_length += dist_from_interval

        return timedelta(microseconds=communication_length)

    def compute_bw_from_comm_len(self, capacity, latency, communication_length):
        """Returns the amount of bandwidth required to allocate to this TA based on the amount of time this TA communicates for

        :param timedelta communication_length: The time this TA communicates for
        :returns Kbps bandwidth_required: The amount of bandwidth this TA requires to communicate
        """
        bandwidth_required = (capacity.value / latency.get_microseconds()) * communication_length.get_microseconds()
        return Kbps(bandwidth_required)

    def discretized_on_current_channel(self, channel):
        """Determines if a TA has been discretized to communicate on a input channel.

        :param Channel channel: The channel to check
        :returns Boolean:
        """
        return channel.frequency.value == self.channel.frequency.value

    def channel_is_eligible(self, channel):
        """Determines if a TA is eligible to communicate on a channel.

        :param Channel channel: The channel to check
        :returns Boolean:
        """
        return any(x.value == channel.frequency.value for x in self.eligible_frequencies)

    def __str__(self):
        channel_print_val = ''
        if self.channel != None:
            channel_print_val = self.channel.frequency.value

        return '<id_: {0}, ' \
               'minimum_voice_bandwidth: {1}, ' \
               'minimum_safety_bandwidth: {2}, ' \
               'total_minimum_bandwidth: {3}, ' \
               'latency: {4}, ' \
               'scaling_factor: {5}, ' \
               'c: {6}, ' \
               'eligible_frequencies: {7}, ' \
               'bandwidth: {8}, ' \
               'channel: {9}, ' \
               'value: {10}, ' \
               'min_value: {11}, ' \
               'max_value: {12}>'.format(
                   self.id_,
                   self.minimum_voice_bandwidth.value,
                   self.minimum_safety_bandwidth.value,
                   self.total_minimum_bandwidth,
                   self.latency.get_microseconds(),
                   self.scaling_factor,
                   self.c,
                   self.eligible_frequencies,
                   self.bandwidth.value,
                   channel_print_val,
                   self.value,
                   self.min_value,
                   self.max_value)

    def __eq__(self, other):
        if isinstance(other, TA):
            return self.id_ == other.id_
        return False

    def __hash__(self):
        return hash(self.id_)
        
    __repr__ = __str__
