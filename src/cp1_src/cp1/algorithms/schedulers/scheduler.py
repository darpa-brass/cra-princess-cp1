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
from cp1.data_objects.mdl.txop import TxOp
from cp1.utils.file_utils import *
from cp1.common.logger import Logger

logger = Logger().logger

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

        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        co = deepcopy(constraints_object)
        self.constraints_object = co
        deadline_window = MDL_MIN_INTERVAL + self.constraints_object.guard_band
        schedules = self._schedule(optimizer_result, deadline_window)
        return schedules

    def compute_max_channel_efficiency(self, optimizer_result):
        """Computes the maximum possible bandwidth efficiency per channel given the TAs assigned to that Channel

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :returns [<float>]: Percentage representing total bandwidth efficiency
        """
        channel_eff = defaultdict(int)

        for channel, tas in optimizer_result.scheduled_tas_by_channel.items():
            guard_bands = 0
            for ta in tas:
                remainder = ((self.constraints_object.epoch.get_microseconds() / 1000) * (1 - (ta.bandwidth.value / ta.channel.capacity.value))) # Remainder of epoch had a TA only needed to speark once
                guard_bands += (2 * math.ceil(remainder / (ta.latency.get_microseconds() / 1000)))

            channel_eff[channel] = ((self.constraints_object.epoch.get_microseconds() / 1000) -  (guard_bands * self.constraints_object.guard_band.get_microseconds() / 1000)) / (self.constraints_object.epoch.get_microseconds() / 1000)

        return channel_eff

    def compute_latency_requirement(self, schedules):
        txops_by_ta = default_dict(list)
        for schedule in schedules:
            for txop in schedule.txops:
                txops_by_ta[ta.id_].append(txop.start_usec)

        for k, v in txops_by_ta.items():
            v.sort(key=lambda x: x.start_usec)

        for k, v in txops_by_ta.items():
            # If this TA has only
            if len(v == 1):
                continue

            for start_time in v:
                pass

    def compute_total_value(self, schedules):
        ta_comm_lens = defaultdict(timedelta)
        for schedule in schedules:
            for txop in schedule.txops:
                ta_comm_lens[txop.ta] += txop.stop_usec - txop.start_usec

        value = 0
        for ta, comm_len in ta_comm_lens.items():
            bw = ta.compute_bw_from_comm_len(capacity=ta.channel.capacity, communication_length=comm_len, latency=ta.latency,)
            value += ta.compute_value_at_bandwidth(bw)
            logger.debug('Value: {0}, Bandwidth: {1}'.format(value, bw))
        return value

    def create_blocks(self, channel, ta_list, min_latency, start_times, block_starts, schedule):
        """ Creates a set of communication blocks for one channel, each of length min_latency amongst the scheduled TAs

        :param Channel channel: The channel to create this schedule on
        :param [<TA>] ta_list: The list of TAs scheduled on this channel
        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param {str, int} start_times: The dictionary of start times formatted as: ID + Direction: milliseconds_time
        :param [<int>] block_starts: The list of times each block starts at. i.e. If [0, 80] is entered, you will get two conservative blocks, one that begins at 0, and one that begins at 80
        :param Schedule schedule: The schedule
        :returns [<TxOp>] txops: A list of TxOps to be scheduled on this channel
        """
        channel_start_time = timedelta(microseconds=0)

        for x in range(len(ta_list)):
            ta = ta_list[x]
            # The time at which a TA can begin communicating is equal to the start
            # time of the channel
            up_start = channel_start_time

            # The amount of time a TA is allowed to communicate is equal to
            # the amount of time it requires for two way communication / 2,
            # without a guard band added in. Guard bands will be added later.
            one_way_transmission_length = ta.compute_communication_length(
            channel.capacity, min_latency, timedelta(microseconds=0)) / 2

            # Stretch out last TA scheduled to communicate on this channel
            if x == len(ta_list) - 1 and one_way_transmission_length > timedelta(microseconds=1000):
                # logger.debug('One of these cases')
                # logger.debug(str(one_way_transmission_length))
                one_way_transmission_length = ((min_latency - up_start) / 2) - (2 * self.constraints_object.guard_band)
                # logger.debug('{0}_{1}_{2}'.format(one_way_transmission_length, min_latency, up_start))
            # Each direction of transmission requires
            up_stop = one_way_transmission_length + channel_start_time
            down_start = up_stop + self.constraints_object.guard_band
            down_stop = down_start + one_way_transmission_length

            # Update the start time of this channel to be the time at which the
            # last TA communicated, plus on guard_band
            channel_start_time = down_stop + self.constraints_object.guard_band

            # We need to record what times a TA last communicated UP and DOWN
            # in order to make sure we are satisfying latency requirements
            # This is only used by the ConservativeScheduler
            start_times[ta.id_ + 'up'] = up_stop
            start_times[ta.id_ + 'down'] = down_stop

            # Create TxOps for each block in blocks
            txops = []
            for x in block_starts:
                txop_up = TxOp(
                    ta=ta,
                    radio_link_id=id_to_mac(ta.id_, 'up'),
                    start_usec=up_start + x,
                    stop_usec=up_stop + x,
                    center_frequency_hz=channel.frequency,
                    txop_timeout=self.constraints_object.txop_timeout)
                txop_down = TxOp(
                    ta=ta,
                    radio_link_id=id_to_mac(ta.id_, 'down'),
                    start_usec=down_start + x,
                    stop_usec=down_stop + x,
                    center_frequency_hz=channel.frequency,
                    txop_timeout=self.constraints_object.txop_timeout)

                schedule.txops.extend([txop_up, txop_down])
