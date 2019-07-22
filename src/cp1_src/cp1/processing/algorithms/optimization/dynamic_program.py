"""dynamic_program.py

A Dynamic Program that schedules TAs.
"""
import time
import numpy
import math
import copy
from pandas import *
from cp1.processing.algorithms.optimization.optimization_algorithm import OptimizationAlgorithm
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.constants.constants import *
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.common.logger import Logger

logger = Logger().logger


class DynamicProgram(OptimizationAlgorithm):
    def __init__(self, constraints_object):
        self.constraints_object = constraints_object
        self.scheduled_tas = []

    def optimize(self, discretization_algorithm, factor=DYNAMIC_PROGRAM_FACTOR):
        """
        i = channel index
        j = num_tas
        k = time in the table
        l = the bandwidth sample for a set of TAs
        :param int factor: The granularity of this solution, 1 kth of a millisecond.
                      i.e. If factor = 2, the schedule will consider schedules at 500 microsecond intervals. If
                           If factor = 3, 330 microsecond intervals.
        """
        print("Beginning Dynamic Program...")
        start_time = time.perf_counter()

        self.scheduled_tas = []
        self.discretization_algorithm = discretization_algorithm
        self.factor = factor

        for i in range(0, len(self.constraints_object.channels)):

            # Remove any TAs that have already been scheduled or are not allowed to be scheduled on this frequency
            eligible_tas = list(filter(lambda x: x.id_ not in set(x.id_ for x in self.scheduled_tas), list(filter(lambda x: x.channel_is_eligible(self.constraints_object.channels[i]), self.constraints_object.candidate_tas))))
            discretized_tas = discretization_algorithm.discretize(eligible_tas, [self.constraints_object.channels[i]])

            # If no TAs are eligible, move to next channel
            if len(eligible_tas) == 0:
                continue

            min_latency = min(eligible_tas, key=lambda x: x.latency.value).latency.value

            # Setup table data for these eligible TAs.
            # Add 1 because we need to account for the case where there are 0 TAs
            # and 0 time (or weight in the knapsack)
            table_width = (min_latency * factor) + 1
            table_height = len(eligible_tas) + 1

            table = [[0 for i in range(table_width)]
                          for j in range(table_height)]

            # Populate table
            for j in range(1, table_height):
                for k in range(0, table_width):
                    if math.ceil(discretized_tas[(j-1) * self.discretization_algorithm.num_discretizations].compute_communication_length(self.constraints_object.channels[i].capacity, Milliseconds(min_latency), self.constraints_object.guard_band)*factor) > k:
                        table[j][k] = table[j-1][k]
                    else:
                        sol = table[j-1][k]
                        for l in range(((j - 1) * discretization_algorithm.num_discretizations), j * discretization_algorithm.num_discretizations):
                            wk = math.ceil(discretized_tas[l].compute_communication_length(self.constraints_object.channels[i].capacity, Milliseconds(min_latency), self.constraints_object.guard_band) * factor)
                            if wk <= k:
                                curr_val = table[j - 1][k-wk] + discretized_tas[l].value
                                if sol < curr_val:
                                    sol = curr_val
                        table[j][k] = sol

            # Prints the dynamic program
            print(DataFrame(table))
            self._retrieve_tas(table, len(eligible_tas), min_latency *
                               factor, i, discretized_tas, min_latency)

        value = sum(ta.value for ta in self.scheduled_tas)
        run_time = time.perf_counter() - start_time

        print("Dynamic Program completed in {0} seconds".format(run_time))
        return AlgorithmResult(constraints_object=self.constraints_object, scheduled_tas=self.scheduled_tas, solve_time=run_time, run_time=run_time,
                                value=value)

    def _retrieve_tas(self, table, row, column, index, discretized_tas, min_latency):
        if row == 0:
            return self.scheduled_tas
        else:
            if table[row][column] == table[row-1][column]:
                return self._retrieve_tas(table, row-1, column, index, discretized_tas, min_latency)
            else:
                for i in range((row-1) * self.discretization_algorithm.num_discretizations, row * self.discretization_algorithm.num_discretizations):
                    wi = math.ceil(discretized_tas[i].compute_communication_length(self.constraints_object.channels[index].capacity, Milliseconds(min_latency), self.constraints_object.guard_band) * self.factor)
                    if wi <= column:
                        if table[row][column] == table[row-1][column-wi] + discretized_tas[i].value:
                            self.scheduled_tas.append(discretized_tas[i])
                            return self._retrieve_tas(table, row-1, column - wi, index, discretized_tas, min_latency)

    def __str__(self):
        return 'DynamicProgram'

    __repr__ = __str__
