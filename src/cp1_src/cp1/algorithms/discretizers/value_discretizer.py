"""value_discretization.py

Discretizes uniformly with respect to min_value.
i.e. disc_count = 100, ta.min_value = 20
ta.compute_value(8000) = 85
85 - 20 = 65
65 / 100 = 6.5
[ta.compute_bandwidth(ta.min_value + 6.5), ta.compute_bandwidth(ta.min_value) + 13 etc...]

Author: Tameem Samawi (tsamawi@cra.com)
"""
import copy
from cp1.data_objects.constants.constants import *
from cp1.algorithms.discretizers.discretizer import Discretizer
from cp1.data_objects.processing.ta import TA


class ValueDiscretizer(Discretizer):
    def __init__(self, disc_count):
        self.disc_count = disc_count

    def _discretize(self, constraints_object):
        discretized_tas = []
        for ta in constraints_object.candidate_tas:
            for channel in constraints_object.channels:
                ta.channel = channel
                discretization_length = (ta.max_value - ta.min_value)/self.disc_count
                for i in range(0, self.disc_count):
                    disc_ta = copy.deepcopy(ta)
                    value = disc_ta.min_value + (i * discretization_length)
                    disc_ta.value = value
                    disc_ta.bandwidth = Kbps(ta.compute_bandwidth_at_value(value))
                    discretized_tas.append(disc_ta)
        return discretized_tas

    def __str__(self):
        return 'ValueDiscretizer'

    __repr__ = __str__
