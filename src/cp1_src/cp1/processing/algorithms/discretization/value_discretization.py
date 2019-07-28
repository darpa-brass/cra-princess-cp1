"""value_discretization.py

Discretizes uniformly with respect to min_value.
i.e. num_discretizations = 100, ta.min_value = 20
ta.compute_value(8000) = 85
85 - 20 = 65
65 / 100 = 6.5
[ta.compute_bandwidth(ta.min_value + 6.5), ta.compute_bandwidth(ta.min_value) + 13 etc...]

Author: Tameem Samawi (tsamawi@cra.com)
"""
import copy
from cp1.data_objects.constants.constants import *
from cp1.processing.algorithms.discretization.discretization_algorithm import DiscretizationAlgorithm
from cp1.data_objects.processing.ta import TA


class ValueDiscretization(DiscretizationAlgorithm):
    def __init__(self, num_discretizations):
        self.num_discretizations = num_discretizations

    def discretize(self, tas, channels):
        discretized_tas = []
        for ta in tas:
            for channel in channels:
                ta.channel = channel
                discretization_length = int(ta.max_value - ta.min_value)/self.num_discretizations
                for i in range(0, self.num_discretizations):
                    disc_ta = copy.deepcopy(ta)
                    value = disc_ta.min_value + (i * discretization_length)
                    disc_ta.value = value
                    disc_ta.bandwidth = Kbps(ta.compute_bandwidth(value))
                    discretized_tas.append(disc_ta)
        return discretized_tas

    def __str__(self):
        return 'ValueDiscretization'

    __repr__ = __str__
