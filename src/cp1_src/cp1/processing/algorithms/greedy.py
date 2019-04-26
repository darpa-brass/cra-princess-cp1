"""greedy.py

Algorithm that greedily selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.processing.algorithms.optimization_algorithm import OptimizationAlgorithm
from cp1.data_objects.processing.algorithm_result import AlgorithmResult


class Greedy(OptimizationAlgorithm):
    def optimize(self, constraints_object):
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

        :param ConstraintsObject constraints_object: A constraints object containing all data needed to perform this optimization.
        """
        start_time = time.perf_time()
        selected_tas = {}
        value = 0
        constraints_object.candidate_tas.sort(key=lambda ta: (
            ta.utility_threshold / ta.total_minimum_bandwidth.value), reverse=True)

        for channel in constraints_object.channels:
            selected_tas[channel] = []
            for ta in candidate_tas:
                partition_bandwidth_requirement = (
                    ta.total_minimum_bandwidth.value / channel.num_partitions * channel.capacity) + (2 * constraints_object.guard_band.value)

                if partition_bandwidth_requirement + channel.first_available_time <= channel.partition_length:
                    selected_tas.get(channel).append(ta)
                    value += ta.utility_threshold
                    channel.first_available_time += partition_bandwidth_requirement
                    channel.value += ta.utility_threshold
                    logger.info('{0} selected for scheduling on frequency {1}'.format(
                        ta.id_, channel.frequency.value))

        run_time = time.perf_time() - start_time
        return AlgorithmResult(selected_tas, solve_time, run_time, value)
