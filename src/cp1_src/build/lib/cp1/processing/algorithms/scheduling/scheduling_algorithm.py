"""scheduling_algorithm.py

Abstract base class for all scheduling algorithms.
"""
import abc
from cp1.common.exception_class import ScheduleAddException
from cp1.common.exception_class import InvalidScheduleException


class SchedulingAlgorithm(abc.ABC):
    @abc.abstractmethod
    def schedule(self, algorithm_result, constraints_object):
        pass

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

        ordered_txops.sort(key=lambda x: x.start_usec.value, reverse=True)
        for i in range(len(ordered_txops)):
            if i == 0:
                continue
            if ordered_txops[i].start_usec.value - ordered_txops[i-1].start_usec.value < self.guard_band.value:
                raise InvalidScheduleException(
                    'Guard band violation: {0} {1}'
                    .format(ordered_txops[i], ordered_txops[i-1]), 'SchedulingAlgorithm.validate')
        return True
