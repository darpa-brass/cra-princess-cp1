"""greedy_optimizer.py

Algorithm that greedily selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
from cp1.utils.decorators.timedelta import timedelta
from cp1.algorithms.optimizers.optimizer import Optimizer
from cp1.data_objects.processing.optimizer_result import OptimizerResult
from cp1.common.logger import Logger

logger = Logger().logger


class GreedyOptimizer(Optimizer):
    def _optimize(self, constraints_object, discretized_tas, deadline_window=None):
        """Greedily selects TAs for scheduling.
        Sorts the candidate TAs based on the ratio between utility threshold and minimum bandwidth.
        Then iterates through the sorted list to schedule TAs on the first available channel.
        A TA requires the total_minimum_bandwidth and twice the guard band
        since TAs require two-way communication; Ground to TA and TA to Ground.

        i.e.
        <ID, Bandwidth, Value>
        [<TA1, 200, 50>, <TA2, 150, 100>, <TA3, 100, 100>, <TA4, 150, 50>, <TA5, 180, 60>]
        Gets sorted to:
        [<TA3, ...>, <TA2, ...>, <TA5, ...>]

        :returns dict{int:[TA]}: A channel frequency and a list of TAs to be scheduled at that frequency.
        """
        logger.debug('Beginning Greedy Optimization...')
        start_time = time.perf_counter()
        scheduled_tas = []

        # Set the assigned bandwidth of each TA to be it's minimum as the
        # Greedy Optimizer only considers TAs at their minimum bandwidths
        for ta in constraints_object.candidate_tas:
            ta.bandwidth = ta.total_minimum_bandwidth

        # Order TAs by the ratio of their value / bandwidth requirement at minimum bandwidth
        # TAs will then be selected based on this ordering, hence the name
        # Greedy Optimizer
        constraints_object.candidate_tas.sort(key=lambda ta: (
                ta.min_value / ta.total_minimum_bandwidth.value), reverse=True)

        for channel in constraints_object.channels:
            channel_start_time = timedelta(microseconds=0)

            # The length of time of each communication block on a channel in a Greedy Optimizer
            # is identical. It is the minimum latency of all TAs scheduled to communicate on
            # this channel. By using the minimum latency, though it is leff efficient, we
            # can gurantee that every scheduled TA using this algorithm can fit within
            # this block
            min_latency = self.retrieve_min_latency(constraints_object.candidate_tas)

            for ta in constraints_object.candidate_tas:

                # Only consider this TA if it has not already been assigned to another
                # channel, and it is eligible to communicate on this channel
                if ta not in scheduled_tas and ta.channel_is_eligible(channel):

                    # The minimum communication requirement is the amount of time
                    # this TA requires when only assigned it's minimum bandwidth
                    min_communication_requirement = ta.compute_communication_length(channel.capacity, min_latency, constraints_object.guard_band)

                    # The TA fits on this channel if the amount of time it requires
                    # does not exceed the length of one block on this channel, while
                    # also taking into consideration that other TAs may have already
                    # been scheduled on this channel already (hence channel_start_time)
                    ta_fits_on_channel = min_communication_requirement + channel_start_time <= min_latency
                    if ta_fits_on_channel:
                        bandwidth = ta.compute_bw_from_comm_len(channel.capacity, min_latency, min_communication_requirement, constraints_object.guard_band)
                        ta.bandwidth = bandwidth
                        ta.value = ta.compute_value_at_bandwidth(bandwidth)
                        ta.channel = channel
                        channel_start_time += min_communication_requirement
                        scheduled_tas.append(ta)

        value = self.compute_solution_value(scheduled_tas)
        run_time = time.perf_counter() - start_time
        logger.debug('Greedy Optimization complete in {0} seconds'.format(run_time))

        return OptimizerResult(scheduled_tas=scheduled_tas, run_time=run_time, solve_time=run_time, value=value)

    def __str__(self):
        return 'GreedyOptimizer'

    __repr__ = __str__
