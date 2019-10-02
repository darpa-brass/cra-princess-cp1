"""accuracy_discretization.py

Provides a gurantee on the accuracy of the overall solution in relation to the optimal solution.
Guaranteed accuracy is: 1 - accuracy
i.e. accuracy = 0.001, therefore guaranteed accuracy is 99.999
disc_count = (1 - 0.001) * (100 / ta.min_value)

Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
import copy
from cp1.data_objects.constants.constants import *
from cp1.algorithms.discretizers.discretizer import Discretizer


class AccuracyDiscretizer(Discretizer):
    def __init__(self, epsilon):
        self.epsilon = epsilon
        self.accuracy = 1 - epsilon

    def _discretize(self, constraints_object):
        discretized_tas = []

        min_value_ta = min(constraints_object.candidate_tas, key=lambda x: (x.min_value / x.scaling_factor))
        min_value = min_value_ta.min_value / min_value_ta.scaling_factor

        self.disc_count = math.ceil(math.log(100/min_value)/math.log(1/(1 - self.accuracy))) + 1

        for ta in constraints_object.candidate_tas:
            for channel in constraints_object.channels:
                ta.channel = channel
                for i in range(0, self.disc_count):
                    value = ta.min_value/math.pow((1 - self.accuracy), i)
                    disc_ta = copy.deepcopy(ta)
                    if value > ta.max_value:
                        disc_ta.value = disc_ta.max_value
                        disc_ta.bandwidth = MAX_BANDWIDTH
                    else:
                        disc_ta.value = value
                        disc_ta.bandwidth = Kbps(disc_ta.compute_bandwidth_at_value(value))
                    discretized_tas.append(disc_ta)
        return discretized_tas

    def __str__(self):
        return 'AccuracyDiscretizer({0})'.format(self.epsilon)

    __repr__ = __str__
