"""dynamic_program.py

A Dynamic Program that schedules TAs.
"""
from time import perf_counter
import numpy
import math
import copy
import itertools
from pandas import *
from cp1.algorithms.optimizers.optimizer import Optimizer
from cp1.data_objects.constants.constants import *
from cp1.data_objects.processing.optimizer_result import OptimizerResult
from cp1.common.logger import Logger
from cp1.utils.decorators.timedelta import timedelta


logger = Logger().logger


class DynamicProgram(Optimizer):
    def _optimize(self, constraints_object, discretized_tas, num_discretizations):
        """
        i = channel index
        j = num_tas
        k = time in the table
        l = the bandwidth sample for a set of TAs
        """
        logger.debug("Beginning Dynamic Program...")
        start_time = perf_counter()
        self.scheduled_tas = []
        self.constraints_object = constraints_object
        self.num_discretizations = num_discretizations

        num_channels = len(constraints_object.channels)
        for channel_index in range(num_channels):
            # Builds one DP table per each channel to schedule TAs over
            channel = constraints_object.channels[channel_index]

            # Remove any TAs that have already been scheduled or are not allowed to be scheduled on this frequency
            unscheduled_tas = list(filter(lambda x: x.id_ not in set(x.id_ for x in self.scheduled_tas), constraints_object.candidate_tas))
            eligible_tas = list(filter(lambda x: x.channel_is_eligible(channel), unscheduled_tas))

            # Apply the same filters to the list of discretized TAs, as that is the list the DynamicProgram will ultimately use
            unscheduled_discretized_tas = list(filter(lambda x: x.id_ not in set(x.id_ for x in self.scheduled_tas), discretized_tas))
            eligible_discretized_tas = list(filter(lambda x: x.discretized_on_current_channel(channel), unscheduled_discretized_tas))

            # If no TAs are eligible, move to next channel
            if len(eligible_tas) != 0:

                channel_min_latency = self.retrieve_min_latency(eligible_tas)

                # Setup table data for these eligible TAs.
                # Table needs to include the possibility that 0 TAs are scheduled at 0 time.
                # Therefore table width and heigth are offset by 1
                table_offset = 1
                table_width = int((channel_min_latency.get_milliseconds() * DYNAMIC_PROGRAM_TABLE_QUANTIZATION) + table_offset)
                table_height = len(eligible_tas) + table_offset

                table = [[0 for channel_index in range(table_width)]
                              for j in range(table_height)]

                # Populate table
                # Each iteration computes the optimal solution for the first ta_set_size number of TAs
                for row in range(table_offset, table_height):

                    # The amount of time available to communicate on the channel
                    for column in range(table_offset, table_width):

                        # Select first discretization of TA, this corresponds to the TA set
                        # to it's minimum_bandwidth_value. If this TA can't fit, no other
                        # discretization of this TA will fit.
                        current_ta = eligible_discretized_tas[int((row - 1) * num_discretizations)]

                        # Compute the communication length for this TA based on the minimum latency for this channel
                        minimum_ta_communication_length = current_ta.compute_communication_length(channel.capacity, channel_min_latency, constraints_object.guard_band)

                        # Convert the communication length to an index in the dynamic program table.
                        # I.e.
                        #    ta_communication_length = timedelta(milliseconds=10)
                        #    DYNAMIC_PROGRAM_TABLE_QUANTIZATION = 2
                        #    table_index = 10 * 2 = 20
                        minimum_required_communication_length_index = minimum_ta_communication_length.get_milliseconds() * DYNAMIC_PROGRAM_TABLE_QUANTIZATION

                        # If the TA to consider requires more communication length than available at this time index, it doesn't fit.
                        # So the best solution is the same as the best solution excluding it. i.e. table[row-1][column]
                        if minimum_required_communication_length_index > column:
                            table[row][column] = table[row-1][column]

                        # If the TA to consider does fit in the table at it's minimum bandwidth
                        else:

                            # Initially, the best value found when considering this TA is the value when not considering this TA
                            best_value_so_far = table[row - table_offset][column]

                            # Then check the rest of it's discretizations
                            for ta_discretization in itertools.islice(eligible_discretized_tas, int((row - 1) * num_discretizations), int(row * num_discretizations)):
                                required_communication_length = ta_discretization.compute_communication_length(channel.capacity, channel_min_latency, constraints_object.guard_band)
                                required_communication_length_index = math.ceil(required_communication_length.get_milliseconds()) * DYNAMIC_PROGRAM_TABLE_QUANTIZATION

                                # Keep track of the highest value provided by scheduling this TA
                                if required_communication_length_index <= column:
                                    value_of_scheduling_discretized_ta = table[row - 1][column - required_communication_length_index] + ta_discretization.value

                                    if value_of_scheduling_discretized_ta > best_value_so_far:
                                        best_value_so_far = value_of_scheduling_discretized_ta

                            table[row][column] = best_value_so_far

                # Prints the dynamic program
                print(DataFrame(table))
                self._compute_solution_path(table, len(eligible_tas), int(channel_min_latency.get_milliseconds() *
                                   DYNAMIC_PROGRAM_TABLE_QUANTIZATION), channel_index, eligible_discretized_tas, channel_min_latency)

        value = self.compute_solution_value(self.scheduled_tas)

        run_time = perf_counter() - start_time
        logger.debug("Dynamic Program completed in {0} seconds".format(run_time))

        return OptimizerResult(scheduled_tas=self.scheduled_tas, solve_time=run_time, run_time=run_time,
                                value=value)

    def _compute_solution_path(self, table, row, column, channel_index, eligible_discretized_tas, channel_min_latency):
        channel = self.constraints_object.channels[channel_index]

        # Base case
        if row == 0:
            return

        else:

            # If the solution using N TAs is the same as the solution using N - 1 TAs,
            # the Nth TA was not scheduled
            if table[row][column] == table[row-1][column]:
                return self._compute_solution_path(table, row-1, column, channel_index, eligible_discretized_tas, channel_min_latency)

            else:

                # Otherwise, the Nth TA was scheduled- find out which discretization it was scheduled at
                for i in range(int((row-1) * self.num_discretizations), int(row * self.num_discretizations)):
                    required_communication_length = eligible_discretized_tas[i].compute_communication_length(channel.capacity, channel_min_latency, self.constraints_object.guard_band)
                    required_communication_length_index = math.ceil(required_communication_length.get_milliseconds() * DYNAMIC_PROGRAM_TABLE_QUANTIZATION)

                    # If the Nth TA's discretization fits
                    if required_communication_length_index <= column:

                        # If the Nth TA's discretization was a solution based on a previous subproblem
                        if table[row][column] == table[row-1][column-required_communication_length_index] + eligible_discretized_tas[i].value:
                            self.scheduled_tas.append(eligible_discretized_tas[i])
                            return self._compute_solution_path(table, row-1, column - required_communication_length_index, channel_index, eligible_discretized_tas, channel_min_latency)

    def __str__(self):
        return 'DynamicProgram'

    __repr__ = __str__
