import time
import numpy
import math
import copy
from pandas import *
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.utils.ta_generator import TAGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.constants.constants import *


class DynamicProgram:
    def __init__(self, constraints_object):
        self.constraints_object = constraints_object
        self.scheduled_tas = []

    def optimize(self, discretization_strategy, factor=DYNAMIC_PROGRAM_FACTOR):
        """
        i = channel index
        j = num_tas
        k = time in the table
        l = the bandwidth sample for a set of TAs
        :param int factor: The granularity of this solution, 1 kth of a millisecond.
                      i.e. If factor = 2, the schedule will consider schedules at 500 microsecond intervals.
                           If factor = 3, the schedule will consider schedules at 330 microsecond intervals.
        """
        start_time = time.perf_counter()

        self.scheduled_tas = []
        self.discretization_strategy = discretization_strategy
        self.factor = factor

        eligible_tas = discretization_strategy.discretize(self.constraints_object.candidate_tas, self.constraints_object.channels)

        for i in range(0, len(self.constraints_object.channels)):
            # Remove any TAs that have already been scheduled or are not allowed to be scheduled on this frequency
            eligible_tas = list(filter(lambda x: x.id_ not in set(x.id_ for x in self.scheduled_tas), list(filter(lambda x: x.channel_is_eligible(self.constraints_object.channels[i]), eligible_tas))))

            # If no TAs are eligible, move to next channel
            if len(eligible_tas) == 0:
                continue

            min_latency = min(eligible_tas, key=lambda x: x.latency.value).latency.value

            # Setup table data for these eligible TAs
            self.tas = discretization_strategy.discretize(eligible_tas, [self.constraints_object.channels[i]])
            self.table_width = (min_latency * factor) + 1
            self.table_height = len(eligible_tas) + 1

            self.table = [[0 for i in range(self.table_width)]
                          for j in range(self.table_height)]

            # Populate table
            for j in range(1, self.table_height):
                for k in range(0, self.table_width):
                    if math.ceil(eligible_tas[j-1].compute_communication_length(self.constraints_object.channels[i].capacity, Milliseconds(min_latency), self.constraints_object.guard_band)*factor) > k:
                        self.table[j][k] = self.table[j-1][k]
                    else:
                        sol = self.table[j-1][k]
                        for l in range(((j - 1) * discretization_strategy.num_discretizations), j * discretization_strategy.num_discretizations):
                            wk = math.ceil((((self.tas[l].bandwidth.value / self.constraints_object.channels[i].capacity.value) * min_latency) + (2 * self.constraints_object.guard_band.value)) * factor)
                            if wk <= k:
                                curr_val = self.table[j -
                                                      1][k-wk] + self.tas[l].value
                                if sol < curr_val:
                                    sol = curr_val
                        self.table[j][k] = sol

            # Prints the dynamic program
            # print(DataFrame(self.table))
            self._retrieve_tas(len(eligible_tas), min_latency *
                               factor, i, self.constraints_object.channels[i].frequency.value,
                               min_latency)

        value = sum(ta.value for ta in self.scheduled_tas)
        run_time = time.perf_counter() - start_time

        return AlgorithmResult(scheduled_tas=self.scheduled_tas, solve_time=run_time, run_time=run_time,
                                value=value)

    def _retrieve_tas(self, row, column, index, frequency, min_latency):
        if row == 0:
            return self.scheduled_tas
        else:
            if self.table[row][column] == self.table[row-1][column]:
                return self._retrieve_tas(row-1, column, index, frequency, min_latency)
            else:
                for i in range((row-1) * self.discretization_strategy.num_discretizations, row * self.discretization_strategy.num_discretizations):
                    wi = math.ceil((((self.tas[i].bandwidth.value / self.constraints_object.channels[index].capacity.value) *
                                     min_latency) + (2 * self.constraints_object.guard_band.value)) * self.factor)
                    if wi <= column:
                        if self.table[row][column] == self.table[row-1][column-wi] + self.tas[i].value:
                            self.scheduled_tas.append(self.tas[i])
                            return self._retrieve_tas(row-1, column - wi, index, frequency, min_latency)

    def __str__(self):
        return 'DynamicProgram'

    __repr__ = __str__
