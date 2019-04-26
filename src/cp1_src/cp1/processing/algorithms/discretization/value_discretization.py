"""value_discretization.py

Discretizes uniformly with respect to utility_threshold.
i.e. num_discretizations = 100, ta.utility_threshold = 20
ta.compute_value(2000) = 85
85 - 20 = 65
65 / 100 = 6.5
[ta.compute_bandwidth(ta.utility_threshold + 6.5), ta.compute_bandwidth(ta.utility_threshold) + 13 etc...]

Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.processing.algorithms.discretization.discretization_strategy import DiscretizationStrategy
from cp1.data_objects.processing.ta import TA


class ValueDiscretization(DiscretizationStrategy):
    def __init__(self, num_discretizations):
        self.num_discretizations = num_discretizations

    def discretize(self, constraints_object):
        tas = []
        for ta in constraints_object.candidate_tas:
            for channel in constraints_object.channels:
                discretization_length = int(ta.compute_value(
                    2000) - ta.utility_threshold)/self.num_discretizations
                for i in range(0, self.num_discretizations):
                    value = ta.total_minimum_bandwidth.value + \
                        (i * discretization_length)
                    tas.append(
                        [ta, value, ta.compute_bandwidth(value), channel.frequency.value])
        return tas

    def discretize_one_channel(self, constraints_object):
        tas = []
        for ta in constraints_object.candidate_tas:
            discretization_length = int(ta.compute_value(
                2000) - ta.utility_threshold)/self.num_discretizations
            for i in range(0, self.num_discretizations):
                value = ta.total_minimum_bandwidth.value + \
                    (i * discretization_length)
                tas.append(
                    [ta, value, ta.compute_bandwidth(value), constraints_object.channels[0].frequency.value])
        return tas
