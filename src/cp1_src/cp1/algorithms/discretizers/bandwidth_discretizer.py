"""bandwidth_discretization.py

Discretizes uniformly with respect to bandwidth.
i.e. disc_count = 100, ta.min_bandwidth = 200
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
from cp1.algorithms.discretizers.discretizer import Discretizer


class BandwidthDiscretizer(Discretizer):
    def __init__(self, disc_count):
        self.disc_count = disc_count

    def _discretize(self, constraints_object):
        discretized_tas = []
        for ta in constraints_object.candidate_tas:
            for channel in constraints_object.channels:
                discretization_length = int(MAX_BANDWIDTH.value - ta.total_minimum_bandwidth.value)/self.disc_count
                for i in range(0, self.disc_count):
                    disc_ta = copy.deepcopy(ta)
                    disc_ta.channel = channel
                    bandwidth = Kbps(disc_ta.total_minimum_bandwidth.value + (i * discretization_length))
                    disc_ta.value = ta.compute_value_at_bandwidth(bandwidth)
                    disc_ta.bandwidth = bandwidth
                    discretized_tas.append(disc_ta)
        return discretized_tas

    def __str__(self):
        return 'BandwidthDiscretizer'

    __repr__ = __str__
