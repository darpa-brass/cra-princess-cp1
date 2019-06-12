"""greedy_optimization.py

Algorithm that greedily selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
from cp1.processing.algorithms.optimization.optimization_algorithm import OptimizationAlgorithm
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.common.logger import Logger

logger = Logger().logger


class GreedyOptimization(OptimizationAlgorithm):
    def __init__(self, constraints_object):
        self.constraints_object = constraints_object

    def optimize(self):
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
        logger.debug('Beginning Greedy Algorithm...')
        start_time = time.perf_counter()
        value = 0
        scheduled_tas = []
        self.constraints_object.candidate_tas.sort(key=lambda ta: (
                ta.min_value / ta.total_minimum_bandwidth.value), reverse=True)

        min_latency = min(self.constraints_object.candidate_tas, key=lambda x: x.latency.value).latency

        for ta in self.constraints_object.candidate_tas:
            for channel in self.constraints_object.channels:
                if ta.channel_is_eligible(channel):
                    comm_length = ta.compute_communication_length(channel.capacity, min_latency, self.constraints_object.guard_band, ta.total_minimum_bandwidth)
                    if comm_length + channel.first_available_time <= self.constraints_object.epoch.value:
                        ta.value = ta.min_value
                        ta.bandwidth = ta.total_minimum_bandwidth
                        ta.channel = channel
                        scheduled_tas.append(ta)
                        channel.first_available_time += comm_length
                        value += ta.min_value
                        channel.value += ta.min_value
                    break

        run_time = time.perf_counter() - start_time
        logger.debug('Greedy Algorithm complete in {0} seconds'.format(run_time))
        return AlgorithmResult(scheduled_tas, run_time, run_time, value)

    def __str__(self):
        return 'Greedy'

    __repr__ = __str__
