"""ta.py

Data object representing a TA.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
from cp1.common.exception_class import ComputeValueException
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId


class TA:
    def __init__(
            self,
            id_,
            minimum_voice_bandwidth,
            minimum_safety_bandwidth,
            scaling_factor,
            c):
        """
        Constructor

        :param MdlId id_: The ID of the TA.
        :param Kbps minimum_voice_bandwidth: The minimum required voice bandwidth to get this TA in the air.
        :param Kbps minimum_safety_bandwidth: The minimum required safety bandwidth to get this TA in the air.
        :param int scaling_factor: The amount by which to scale the overall value by onc.
        :param int c: The coefficient of a sample value function. For now it's set to 1 because there is no real value
                  function.
        """
        self.id_ = id_
        self.minimum_voice_bandwidth = minimum_voice_bandwidth
        self.minimum_safety_bandwidth = minimum_safety_bandwidth
        self.total_minimum_bandwidth = Kbps(
            minimum_voice_bandwidth.value + minimum_safety_bandwidth.value)
        self.scaling_factor = float(scaling_factor)
        self.c = float(c)
        self.utility_threshold = self.compute_value(
            self.total_minimum_bandwidth.value)

    def compute_bandwidth(self, utility):
        """
        Computes bandwidth as a function of value."""
        # utility in the function headder is kind of confusing because its actually taking in a percent utility (between 0 and 100) basically dividing out the scaling factor
        # new #
        if utility < self.utility_threshold/self.scaling_factor:
            return 0
        if utility <= self.compute_value(2000)/self.scaling_factor:
            return -math.log((100 - utility)/100)/self.c
        else:
            return 2000
        #### Old #####
        #Tyler: this needs to be a branched function just like the value function which it is the inverse of
        # return (-1 / self.c) * \
        #     math.log((100 - utility / self.scaling_factor) / 100)

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
        if x < self.total_minimum_bandwidth.value:
            return 0.0
        elif x < 2000:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * x)))
        else:
            return self.scaling_factor * \
                (100 - 100 * (math.e ** (-self.c * 2000)))

    def __str__(self):
        return '<id_: {0}, ' \
               'total_minimum_bandwidth: {1}, ' \
               'minimum_voice_bandwidth: {2}, ' \
               'minimum_safety_bandwidth: {3}, ' \
               'scaling_factor: {4}, ' \
               'c: {5}, ' \
               'utility_threshold: {6}>'.format(
               self.id_.value,
               self.total_minimum_bandwidth,
               self.minimum_voice_bandwidth.value,
               self.minimum_safety_bandwidth.value,
               self.scaling_factor,
               self.c,
               self.utility_threshold)

    def __eq__(self, other):
        if isinstance(other, TA):
            return (self.id_ == other.id_ and
                    self.minimum_voice_bandwidth == other.minimum_voice_bandwidth and
                    self.minimum_safety_bandwidth == other.minimum_safety_bandwidth and
                    self.total_minimum_bandwidth == other.total_minimum_bandwidth and
                    self.scaling_factor == other.scaling_factor and
                    self.c == other.c and
                    self.utility_threshold == other.utility_threshold)
        return False

    __repr__ = __str__
