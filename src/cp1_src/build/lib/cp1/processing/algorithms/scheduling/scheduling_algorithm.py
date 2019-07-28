"""scheduling_algorithm.py

Abstract base class for all scheduling algorithms.
"""
import abc
from cp1.common.exception_class import ScheduleAddException
from cp1.common.exception_class import InvalidScheduleException
from collections import defaultdict
import math
from datetime import timedelta


class SchedulingAlgorithm(abc.ABC):
    @abc.abstractmethod
    def schedule(self, algorithm_result, constraints_object):
        """
        :param AlgorithmResult algorithm_result: The algorithm result to create a schedule from
        :param ConstraintsObject constraints_object: The constraints object used to select TAs from

        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        pass

    def bw_efficiency_upper_bound(self, algorithm_result):
        """Computes the maximum possible bandwidth efficiency per channel given the TAs assigned to that Channel

        :param AlgorithmResult algorithm_result: The algorithm result to create a schedule from

        :returns float: Percentage representing total bandwidth efficiency
        """
        channel_to_tas = defaultdict(list)
        channel_eff = defaultdict(int)
        for ta in algorithm_result.scheduled_tas:
            channel_to_tas[ta.channel.frequency.value].append(ta)

        for channel, tas in channel_to_tas.items():
            guard_bands = 0
            for ta in tas:
                remainder = ((algorithm_result.constraints_object.epoch.microseconds / 1000) * (1 - (ta.bandwidth.value / ta.channel.capacity.value))) # Remainder of epoch had a TA only needed to speark once
                guard_bands += (2 * math.ceil(remainder / (ta.latency.microseconds / 1000)))

            channel_eff[channel] = ((algorithm_result.constraints_object.epoch.microseconds / 1000) -  (guard_bands * algorithm_result.constraints_object.guard_band.microseconds / 1000)) / (algorithm_result.constraints_object.epoch.microseconds / 1000)

        return channel_eff
        
    def compute_total_value(self, txop_list):
        """Computes the total value a TA provides at a certain bandwidth

        :param [<TxOp>] txop_list: The list of TxOp nodes that represent an MDL schedule
        """
        txops_by_channel = defaultdict(list)
        for txop in txop_list:
            txops_by_ta[txop.ta.id_].append(txop)

        for ta_id, txops in txops_by_channel.items():
            ta_communication_time = 0
            for txop in txops:
                ta_communication_time += txop.stop_usec - txop.start_usec

            ta_communication_time_ms = ta_communication_time.microseconds / 1000
            ta_bandwidth = txops[0].ta.channel.capacity.value / ta_communication_time_ms
            ta_value = txops[0].ta.compute_value(ta_bandwidth)
            print(ta_value)

    def validate(self, txop_list):
        """Validates schedule against errors such as exceeding the epoch.
        """
        ordered_txops = []
        for txop in txop_list:
            ordered_txops.append(txop)
            if txop.start_usec.toSeconds() > self.epoch.toSeconds():
                raise InvalidScheduleException(
                    'Schedule not allowed to exceed epoch. Found start time of: {0}'.format(
                        txop.start_usec),
                    'SchedulingAlgorithm.validate')
            elif txop.stop_usec.toSeconds() > self.epoch.toSeconds():
                raise InvalidScheduleException(
                    'Schedule not allowed to exceed epoch. Found stop time of: {0}'.format(
                        txop.stop_usec),
                    'SchedulingAlgorithm.validate')
            elif txop.start_usec.toSeconds() < 0:
                raise InvalidScheduleException(
                    'Negative start times not allowed. Found negative start time of: {0}'.format(
                        txop.start_usec),
                    'SchedulingAlgorithm.validate')
            elif txop.stop_usec.toSeconds() < 0:
                raise InvalidScheduleException(
                    'Negative stop times not allowed. Found negative stop time of: {0}'.format(
                        txop.stop_usec),
                    'SchedulingAlgorithm.validate')
            elif txop.start_usec.toSeconds() > txop.stop_usec.toSeconds():
                raise InvalidScheduleException(
                    'Start must be less than stop. Attempted to input a start time of: {0} stop time of: {1}'
                    .format(txop.start_usec, txop.stop_usec), 'SchedulingAlgorithm.validate')

        ordered_txops.sort(key=lambda x: x.start_usec, reverse=True)
        self._validate_guardband(txop_list)
        self._validate_throughput(txop_list)
        self._validate_latency(txop_list)
        return True

    def _validate_guardband(self, txop_list):
        """Checks for guard band violations

        :param [<TxOp>] txop_list: The list of TxOp nodes that represent an MDL schedule
        :raise: InvalidScheduleException
        """
        for i in range(len(txop_list)):
            if i == 0:
                continue
            if txop_list[i].start_usec - txop_list[i-1].start_usec < self.guard_band:
                raise InvalidScheduleException(
                    'Guard band violation: {0} {1}'
                    .format(txop_list[i], txop_list[i-1]), 'SchedulingAlgorithm.validate')

    def _validate_throughput(self, txop_list):
        """Checks that current channel throughput has not been exceeded

        :param [<TxOp>] txop_list: The list of TxOp nodes that represent an MDL schedule
        :raise: InvalidScheduleException
        """
        txops_by_channel = defaultdict(list)
        for txop in txop_list:
            txops_by_ta[txop.ta.channel.frequency].append(txop)

        for frequency, txops in txops_by_channel.items():
            curr_channel_throughput = 0
            for txop in txops:
                curr_channel_throughput += txop.stop_usec - txop.start_usec

            if curr_channel_throughput > constraints_object.epoch.microseconds / 1000000:
                raise InvalidScheduleException(
                    'Channel throughput violation: {0}'
                    .format(txops)
                )


    def _validate_latency(self, txop_list):
        """Checks for latency violations

        :param [<TxOp>] txop_list: The list of TxOp nodes that represent an MDL schedule
        :raise: InvalidScheduleException
        """
        txops_by_ta = defaultdict(list)
        for txop in txop_list:
            txops_by_ta[txop.ta.id_].append(txop)

        for ta_id, txops in txops_by_ta.items():
            curr_txop = txops[0]
            for i in range(1, len(txop_list)):
                if txops[i].start_usec - curr_txop.stop_usec > curr_txop.ta.latency:
                    raise InvalidScheduleException(
                        'Latency violation: {0} {1}'
                        .format(txops[i], curr_txop)
                    )
                curr_txop = txops[i]

    def deconflict_start_deadlines(self, queue, curr_job, timer):
        queue.sort(key=lambda job: job.start_deadline, reverse=True)

        for job in queue:
            if curr_job.start_deadline > job.start_deadline - \
                    DEADLINE_WINDOW and curr_job.start_deadline < job.start_deadline + DEADLINE_WINDOW:
                curr_job.start_deadline = job.start_deadline - DEADLINE_WINDOW

        queue.sort(key=lambda job: job.start_deadline, reverse=False)
        return curr_job
