"""bandwidth_discretization.py

Discretizes uniformly with respect to bandwidth.
i.e. num_discretizations = 100, ta.min_bandwidth = 200
8000 - 200 = 1800
1800 / 100 = 180
[200, 380, 560, 740, 820, 1000...]

Author: Tameem Samawi (tsamawi@cra.com)
"""
import copy
from cp1.data_objects.constants.constants import *
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.processing.algorithms.discretization.discretization_algorithm import DiscretizationAlgorithm


class BandwidthDiscretization(DiscretizationAlgorithm):
    def __init__(self, num_discretizations):
        self.num_discretizations = num_discretizations

    def discretize(self, tas, channels):
        discretized_tas = []
        for ta in tas:
            for channel in channels:
                discretization_length = int(MAX_BANDWIDTH.value - ta.total_minimum_bandwidth.value)/self.num_discretizations
                for i in range(0, self.num_discretizations):
                    disc_ta = copy.deepcopy(ta)
                    disc_ta.channel = channel
                    bandwidth = disc_ta.total_minimum_bandwidth.value + (i * discretization_length)
                    disc_ta.value = ta.compute_value(bandwidth)
                    disc_ta.bandwidth = Kbps(bandwidth)
                    discretized_tas.append(disc_ta)
        return discretized_tas

    def __str__(self):
        return 'BandwidthDiscretization'

    __repr__ = __str__
