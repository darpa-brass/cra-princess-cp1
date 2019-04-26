"""bandwidth_discretization.py

Discretizes uniformly with respect to bandwidth.
i.e. num_discretizations = 100, ta.min_bandwidth = 200
2000 - 200 = 1800
1800 / 100 = 180
[200, 380, 560, 740, 820, 1000...]

Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.processing.algorithms.discretization.discretization_strategy import DiscretizationStrategy


class BandwidthDiscretization(DiscretizationStrategy):
    def __init__(self, num_discretizations):
        self.num_discretizations = num_discretizations

    def discretize(self, constraints_object):
        tas = []
        for ta in constraints_object.candidate_tas:
            for channel in constraints_object.channels:
                discretization_length = int(
                    2000 - ta.total_minimum_bandwidth.value)/self.num_discretizations
                for i in range(0, self.num_discretizations):
                    bandwidth = ta.total_minimum_bandwidth.value + \
                        (i * discretization_length)
                    tas.append(
                        [ta, ta.compute_value(bandwidth), bandwidth, channel.frequency.value])
        return tas

    def discretize_one_channel(self, constraints_object):
        tas = []
        for ta in constraints_object.candidate_tas:
            discretization_length = int(
                2000 - ta.total_minimum_bandwidth.value)/self.num_discretizations
            for i in range(0, self.num_discretizations):
                bandwidth = ta.total_minimum_bandwidth.value + \
                    (i * discretization_length)
                tas.append(
                    [ta, ta.compute_value(bandwidth), bandwidth, constraints_object.channels[0].frequency.value])
        return tas
