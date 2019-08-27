"""conservative_scheduler.py

Constructs TxOps to add to the schedule based on the minimum latency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.utils.decorators.timedelta import timedelta
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.schedule import Schedule
from cp1.algorithms.schedulers.scheduler import Scheduler
from cp1.utils.file_utils import *
from collections import defaultdict


class ConservativeScheduler(Scheduler):
    def schedule(self, constraints_object, optimizer_result, deadline_window=None):
        """Schedules TxOp nodes to communicate at specific times based on constraints such as
        TA latency, channel throughput, channel capacity and epoch length.

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param timedelta deadline_window: The time by which to set a SchedulingJob back in case it's start_deadline conflicts with another job. Only relevant for HybridSchedule.
        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        schedules = []
        for channel, tas in optimizer_result.scheduled_tas.items():
            schedule = Schedule(channel=channel, txops=[])

            for x in range(len(tas)):
                ta = tas[x]

                up_start = channel.start_time
                one_way_transmission_length = ta.compute_communication_length(channel.capacity, channel.min_latency, timedelta(microseconds=0)) / 2
                if x == len(tas) - 1: # Stretch out last communication block
                    one_way_transmission_length = (
                    (channel_min_latencies[channel.frequency.value] - up_start) / 2) - constraints_object.guard_band

                up_stop = one_way_transmission_length + channel.start_time
                down_start = up_stop + constraints_object.guard_band
                down_stop = down_start + one_way_transmission_length

                channel.start_time = down_stop + constraints_object.guard_band
                for x in range(channel.num_partitions):
                    partition_offset = x * channel.partition_length
                    txop_up = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'up'),
                        start_usec=partition_offset + up_start,
                        stop_usec=partition_offset + up_stop,
                        center_frequency_hz=channel.frequency,
                        txop_timeout=constraints_object.txop_timeout)
                    txop_down = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'down'),
                        start_usec=partition_offset + down_start,
                        stop_usec=partition_offset + down_stop,
                        center_frequency_hz=channel.frequency,
                        txop_timeout=constraints_object.txop_timeout)

                    schedule.txop_list.extend([txop_up, txop_down])

            schedules.append(schedule)
        return schedules

    def __str__(self):
        return 'GreedySchedule'
