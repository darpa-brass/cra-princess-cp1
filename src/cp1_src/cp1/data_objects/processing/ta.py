"""ta.py

Data object representing a TA.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
from cp1.common.exception_class import ComputeValueException
from cp1.common.exception_class import ComputeBandwidthException
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.constants.constants import *


class TA:
    def __init__(
            self,
            id_,
            minimum_voice_bandwidth,
            minimum_safety_bandwidth,
            latency,
            scaling_factor,
            c,
            eligible_channels=None,
            bandwidth=None,
            value=None,
            channel=None):
        """
        Constructor

        :param str id_: The ID of the TA.
        :param Kbps minimum_voice_bandwidth: The minimum required voice bandwidth to get this TA in the air.
        :param Kbps minimum_safety_bandwidth: The minimum required safety bandwidth to get this TA in the air.
        :param Milliseconds latency: The maximum delay between radio transmissions
        :param int scaling_factor: The amount by which to scale the overall value by onc.
        :param int c: The coefficient of a sample value function. For now it's set to 1 because there is no real value
                  function.
        :param List[Frequency] eligible_channels: The list of channels communication is permissible over.
        :param Kbps bandwidth: The amount of bandwidth assigned to this TA
        :param int value: The amount of value this TA provides at a some bandwidth
        :param int max_value: The value this TA provides at MAX_BANDWIDTH
        """
        self.id_ = id_
        self.minimum_voice_bandwidth = minimum_voice_bandwidth
        self.minimum_safety_bandwidth = minimum_safety_bandwidth
        self.total_minimum_bandwidth = Kbps(
            minimum_voice_bandwidth.value + minimum_safety_bandwidth.value)
        self.latency = latency
        self.scaling_factor = float(scaling_factor)
        self.c = float(c)
        self.eligible_channels = eligible_channels
        self.bandwidth = bandwidth
        self.value = value
        self.min_value = self.compute_value(self.total_minimum_bandwidth.value)
        self.max_value = self.compute_value(MAX_BANDWIDTH)

    def compute_bandwidth(self, x):
        """
        Computes bandwidth as a function of value."""

        if x < 0:
            raise ComputeBandwidthException(
                'Value must be greater than 0: {0}'.format(x),
                'TA.compute_bandwidth')
        elif x < self.min_value:
            return 0
        elif x < self.max_value:
            return -math.log(1 - (x/(100*self.scaling_factor))) / self.c
        else:
            return MAX_BANDWIDTH

    def compute_value(self, x):
        """Computes value as a function of bandwidth.
        If the provided bandwidth is less than the total minimum bandwidth, which is the
        sum of the safety and voice bandwidth requirements, this TA provides 0 value.
        It is impossible to assign over 2000 Kbps to a given TA, so this equation
        caps out at that value.

        :param int x: The amount of bandwidth allocated to this TA.
        :returns int value: The value this TA provides at that bandwidth.
        """
        if x < 0:
            raise ComputeValueException(
                'Bandwidth must be greater than 0: {0}'.format(x),
                'TA.compute_value')
        elif x < self.total_minimum_bandwidth.value:
            return 0.0
        elif x < MAX_BANDWIDTH:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * x)))
        else:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * MAX_BANDWIDTH)))

    def channel_is_eligible(self, channel):
        return any(x.frequency.value == channel.frequency.value for x in self.eligible_channels)

    def compute_communication_length(self, capacity, latency, guard_band, bandwidth=None):
        if bandwidth is None:
            length = ((self.bandwidth.value / capacity.value) * latency.value) + (2 * guard_band.value)
        else:
            length = ((bandwidth.value / capacity.value) * latency.value) + (2 * guard_band.value)
        return length

    def __str__(self):
        return '<id_: {0}, ' \
               'minimum_voice_bandwidth: {1}, ' \
               'minimum_safety_bandwidth: {2}, ' \
               'total_minimum_bandwidth: {3}, ' \
               'latency: {4}, ' \
               'scaling_factor: {5}, ' \
               'c: {6}, ' \
               'eligible_channels: {7}, ' \
               'bandwidth: {8}, ' \
               'value: {9}, ' \
               'min_value: {10}, ' \
               'max_value: {11}>'.format(
                   self.id_,
                   self.minimum_voice_bandwidth.value,
                   self.minimum_safety_bandwidth.value,
                   self.total_minimum_bandwidth,
                   self.latency.value,
                   self.scaling_factor,
                   self.c,
                   self.eligible_channels,
                   self.bandwidth,
                   self.value,
                   self.min_value,
                   self.max_value)

    def __eq__(self, other):
        if isinstance(other, TA):
            return (self.id_ == other.id_ and
                    self.minimum_voice_bandwidth == other.minimum_voice_bandwidth and
                    self.minimum_safety_bandwidth == other.minimum_safety_bandwidth and
                    self.total_minimum_bandwidth == other.total_minimum_bandwidth and
                    self.latency == other.latency and
                    self.scaling_factor == other.scaling_factor and
                    self.c == other.c and
                    self.eligible_channels == other.eligible_channels and
                    self.bandwidth == other.bandwidth and
                    self.value == other.value and
                    self.min_value == other.min_value and
                    self.max_value == other.max_value)
        return False

    __repr__ = __str__
