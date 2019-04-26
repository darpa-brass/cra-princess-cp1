import numpy
import math
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


class DynamicProgram:
    def __init__(self, discretization_strategy, constraints_object, factor):
        self.discretization_strategy = discretization_strategy
        self.constraints_object = constraints_object
        self.factor = factor
        self.sol = {}
        for channel in constraints_object.channels:
            self.sol[channel.frequency.value] = []
        self.optimize()

    def optimize(self):
        """
        i = channel index
        j = num_tas
        k = time in the table
        l = the bandwidth sample for a set of TAs
        :param int k: The granularity of this solution, 1 kth of a millisecond.
                      i.e. If k = 2, the schedule will consider schedules at 500 microsecond intervals.
                      If k = 3, the schedule will consider schedules at 330 microsecond intervals.
        """
        remaining_tas = self.constraints_object

        for i in range(0, len(self.constraints_object.channels)):
            for k, v in self.sol.items():
                num_popped = 0
                for x in range(0, len(remaining_tas.candidate_tas)):
                    for ta in v:
                        if ta[0].id_ == remaining_tas.candidate_tas[x-num_popped].id_:
                            remaining_tas.candidate_tas.pop(x-num_popped)
                            num_popped += 1
                            break
            self.tas = self.discretization_strategy.discretize_one_channel(remaining_tas)
            self.table_width = (self.constraints_object.latency.value * self.factor) + 1
            self.table_height = len(remaining_tas.candidate_tas) + 1

            self.table = [[0 for i in range(self.table_width)] for j in range(self.table_height)]

            for j in range(1, self.table_height):
                for k in range(0, self.table_width):
                    if math.ceil((((remaining_tas.candidate_tas[j-1].total_minimum_bandwidth.value / self.constraints_object.channels[i].capacity.value) * self.constraints_object.channels[i].latency.value) + (2 * self.constraints_object.guard_band.value))*self.factor) > k:
                        # print('i: {0}'.format(i))
                        # print('j: {0}'.format(j))
                        self.table[j][k] = self.table[j-1][k]
                    else:
                        sol = self.table[j-1][k]
                        for l in range(((j - 1) * self.discretization_strategy.num_discretizations), j * self.discretization_strategy.num_discretizations):
                            wk = math.ceil((((self.tas[l][2] / self.constraints_object.channels[i].capacity.value) * self.constraints_object.channels[i].latency.value) + (2* self.constraints_object.guard_band.value)) * self.factor)
                            if wk <= k:
                                curr_val = self.table[j-1][k-wk] + self.tas[l][1]
                                if sol < curr_val:
                                    sol = curr_val
                        self.table[j][k] = sol
            #print(DataFrame(self.table))
            self._retrieve_tas(len(remaining_tas.candidate_tas), self.constraints_object.latency.value * self.factor, i, self.constraints_object.channels[i].frequency.value)
        return self.sol

    def _retrieve_tas(self, row, column, index, frequency):
        if row == 0:
            return self.sol
        else:
            if self.table[row][column] == self.table[row-1][column]:
                return self._retrieve_tas(row-1, column, index, frequency)
            else:
                for i in range((row-1) * self.discretization_strategy.num_discretizations, row * self.discretization_strategy.num_discretizations):
                    wi = math.ceil((((self.tas[i][2] / self.constraints_object.channels[index].capacity.value) * self.constraints_object.channels[index].latency.value) + (2 * self.constraints_object.guard_band.value)) * self.factor)
                    if wi <= column:
                        if self.table[row][column] == self.table[row-1][column-wi] + self.tas[i][1]:
                            self.sol.get(frequency).append(self.tas[i])
                            return self._retrieve_tas(row-1, column - wi, index, frequency)
