"""conservative_scheduler.py

Constructs TxOps to add to the schedule based on the minimum latency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
from cp1.utils.decorators.timedelta import timedelta
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.schedule import Schedule
from cp1.algorithms.schedulers.scheduler import Scheduler
from cp1.utils.file_utils import *
from collections import defaultdict


class ConservativeScheduler(Scheduler):
    def _schedule(self, optimizer_result, deadline_window=None):
        """Schedules TxOp nodes to communicate at specific times based on constraints such as
        TA latency, channel throughput, channel capacity and epoch length.

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param timedelta deadline_window: The time by which to set a SchedulingJob back in case it's start_deadline conflicts with another job. Only relevant for HybridSchedule.
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        schedules = []
        start_times = {}
        for channel, tas in optimizer_result.scheduled_tas_by_channel.items():
            schedule = Schedule(channel=channel, txops=[])

            # The amount of blocks required is equal to the min_latency
            # / epoch. The length of each block is min_latency.
            # i.e. min_latency = 25 milliseconds
            #      epoch = 100 milliseconds
            #      num_partitions = 100 / 20 = 5
            #      block_starts = [0, 25, 50, 75]
            block_starts = []
            min_latency = min(tas, key=lambda ta: ta.latency).latency
            num_partitions = math.floor(self.constraints_object.epoch / min_latency)

            for x in range(num_partitions):
                block_starts.append(x * min_latency)

            self.create_blocks(channel, tas, min_latency, start_times, block_starts, schedule)
            schedules.append(schedule)

        return schedules

    def __str__(self):
        return 'ConservativeScheduler'
