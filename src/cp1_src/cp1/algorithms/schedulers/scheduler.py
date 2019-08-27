"""scheduler.py

Abstract base class for all scheduling algorithms.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc
import math
from copy import deepcopy
from cp1.utils.decorators.timedelta import timedelta
from collections import defaultdict
from cp1.data_objects.constants.constants import *
from cp1.common.exception_class import ScheduleAddException
from cp1.common.exception_class import InvalidScheduleException


class Scheduler(abc.ABC):
    @abc.abstractmethod
    def _schedule(self, constraints_object, optimizer_result, deadline_window):
        """Schedules TxOp nodes to communicate at specific times based on constraints such as
        TA latency, channel throughput, channel capacity and epoch length.

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param timedelta deadline_window: The time by which to set a SchedulingJob back in case it's start_deadline conflicts with another job. Only relevant for HybridSchedule.
        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        pass

    def schedule(self, constraints_object, optimizer_result):
        """Schedules on a deepcopy of the constraints_object. Returns an empty array if no TAs have been scheduled.

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        co = deepcopy(constraints_object)
        deadline_window = MDL_MIN_INTERVAL + constraints_object.guard_band
        schedules = self._schedule(co, optimizer_result, deadline_window)

        return schedules

    def compute_max_channel_efficiency(self, constraints_object, optimizer_result):
        """Computes the maximum possible bandwidth efficiency per channel given the TAs assigned to that Channel

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :returns [<float>]: Percentage representing total bandwidth efficiency
        """
        channel_eff = defaultdict(int)

        for channel, tas in optimizer_result.scheduled_tas.items():
            guard_bands = 0
            for ta in tas:
                remainder = ((constraints_object.epoch.microseconds / 1000) * (1 - (ta.bandwidth.value / ta.channel.capacity.value))) # Remainder of epoch had a TA only needed to speark once
                guard_bands += (2 * math.ceil(remainder / (ta.latency.microseconds / 1000)))

            channel_eff[channel] = ((constraints_object.epoch.microseconds / 1000) -  (guard_bands * constraints_object.guard_band.microseconds / 1000)) / (constraints_object.epoch.microseconds / 1000)

        return channel_eff
