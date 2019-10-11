"""hybrid_scheduler.py

Constructs TxOps to add to the schedule based on a variation of OS Scheduling.
Authos: Tameem Samawi (tsamawi@cra.com)
"""

import time
from cp1.utils.decorators.timedelta import timedelta
from collections import defaultdict
from cp1.common.logger import Logger
from cp1.common.exception_class import *
from cp1.utils.file_utils import *
from cp1.algorithms.schedulers.scheduler import Scheduler
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.constants.constants import *
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.processing.scheduling_job import SchedulingJob
from cp1.data_objects.processing.optimizer_result import OptimizerResult
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.schedule import Schedule

logger = Logger().logger


class HybridScheduler(Scheduler):
    def _schedule(self, optimizer_result, deadline_window):
        """Calls a ConservativeScheduler for two min_latency blocks, and an OS schedule for the rest

        :param OptimizerResult optimizer_result: The algorithm result to create a schedule from
        :param timedelta deadline_window: The time by which to set a SchedulingJob back in case it's start_deadline conflicts with another job. Only relevant for HybridScheduler.
        :returns [<Schedule>] schedule: A list of Schedule objects for each channel TAs have been scheduled on
        """
        try:
            self._validate_latency_requirement(optimizer_result)
        except InvalidLatencyRequirementException as err:
            logger.exception(err)

        # Calculate the minimum latency for each channel
        schedules = []
        start_times = {}
        min_latency = min(ta.latency for ta in optimizer_result.scheduled_tas)
        for channel, ta_list in optimizer_result.scheduled_tas_by_channel.items():
            # Only run if there are scheduled TAs
            if ta_list:
                schedule = Schedule(channel=channel, txops=[])
                self._wraparound_blocks(channel, ta_list, min_latency, start_times, schedule)
                self._os_schedule_blocks(channel, ta_list, min_latency, start_times, schedule, deadline_window)
                self._extend_final_os_schedule_block(schedule)
                schedules.append(schedule)

        return schedules

    def _wraparound_blocks(self, channel, ta_list, min_latency, start_times, schedule):
        """Places two conservative blocks at the beginnings and ends of the channel

        :param Channel channel: The channel to schedule on
        :param [<TA>] ta_list: The list of TAs scheduled to communicate on this channel
        :param timedelta min_latency: The minimum latency TA scheduled on this channel
        :param {str: timedelta} start_times: The list of times that TAs start communicating.
                                             This is also formatted by their direction. i.e.
                                             {TA7up: timedelta(microseconds=500)}
                                             This means TA7 communicates in the up
                                             direction at 500 microseconds
        :param Schedule schedule: The schedule to modify

        :returns [<TxOp>] txops: The list of created TxOp nodes
        """
        first_wraparound_block = timedelta(microseconds=0)
        last_wraparound_block = self.constraints_object.epoch - min_latency
        block_starts = [first_wraparound_block, last_wraparound_block]

        self.create_blocks(channel, ta_list, min_latency, start_times, block_starts, schedule)

    def _os_schedule_blocks(self, channel, ta_list, min_latency, start_times, schedule, deadline_window):
        # Initially, we must add one scheduling job per each TA to the queue based
        # on that TAs minimum required latency, and the last time it communicated
        # as scheduled in the _wraparound_blocks() function. In case there is a conflict
        # in the required time each TA must communicate by in order to meet its latency
        # requirements, the scheduling job for that TA is moved earlier, by
        # a constant we've named deadline_window.
        # deadline_window, as defined in the cp1.data_objects.constants.constants class,
        # is the MDL_MIN_INTERVAL + the Guard Band for this constraints object.
        queue = self._initialize_queue(
            channel,
            ta_list,
            start_times,
            min_latency,
            deadline_window)

        # The time at which the _wraparound_blocks() function stopped scheduling TAs
        # to communicate over this channel is equal to the minimum latency TA
        # on this channel. Therefore, we start the timer at this timestep.
        timer_start = min_latency
        timer = timer_start

        # The beginning of the second greedy block for this channel is
        # the minimum latency on this channel - the epoch.
        timer_end = self.constraints_object.epoch - min_latency


        # Only run the hybrid scheduler within the end of the first greedy
        # block and the beginning of the last greedy block
        while timer <= timer_end:

            # If there are no jobs left to schedule
            if len(queue) == 1:
                break

           # Find the smallest start_deadline job with a release date less
           # than the timer
            curr_job = queue.pop(0)
            if curr_job.release_date > timer:
                curr_job.release_date = timer

            # Figure out how long this job should run for
            tau = timer
            next_start_deadline = queue[0].start_deadline
            end_time_of_curr_job = tau + curr_job.job_length + self.constraints_object.guard_band
            timer = min(end_time_of_curr_job, next_start_deadline, timer_end)

            # If we have scheduled all the way up until the end of the hybrid scheduler,
            # then we are done scheduling
            if timer == timer_end and tau == timer_end:
                break

            # If the end of the current job's job_length conflicts with the next job's start deadline
            if timer == next_start_deadline and next_start_deadline != end_time_of_curr_job:
                length = curr_job.ta.compute_communication_length(channel.capacity, curr_job.ta.latency)
                job_length = (2 * length) - (timer-tau-self.constraints_object.guard_band)
            else:
                job_length = curr_job.ta.compute_communication_length(channel.capacity, curr_job.ta.latency)

            updated_job = SchedulingJob(
                    ta=curr_job.ta,
                    job_length=job_length / 2,
                    start_deadline=timer + curr_job.ta.latency,
                    release_date=curr_job.release_date + curr_job.ta.latency,
                    direction=curr_job.direction)

            # If we have exceeded the hybrid block, this channel is complete
            if updated_job.start_deadline >  start_times[updated_job.ta.id_ + updated_job.direction] + timer_end:
                continue

            # If this job is due to be scheduled within the final greedy block,
            # then push it's start deadline to be the beginning of the greedy block
            if updated_job.start_deadline > timer_end:
                updated_job.start_deadline = timer_end
            self._deconflict_start_deadlines(
                queue, updated_job, timer, deadline_window)

            # If the job start deadline is not too close to the current time
            # then we are able to append it to the list of jobs
            # This check is here to ensure that the _deconflict_start_deadlines
            # method has not pushed back this job into the past.
            if updated_job.start_deadline >= timer + deadline_window:
                queue.append(updated_job)
            # Append this job to the queue. At this point the updated_job
            # represents an amount of communication in order for this Test Aircraft
            # to meet it's minimum throughput. With a modified Start Deadline property
            # representing the time by which it must begin communication in order to
            # meet it's maximum latency requirement.
            # We then sort the queue again so that our scheduling policy remains
            # that the next job to schedule should be the job with the minimum
            # start deadline
            queue.sort(key=lambda job: job.start_deadline)

            # Construct a TxOp node from the current job and add it to the schedule
            self._add_txop_to_schedule(
                curr_job,
                schedule,
                timer,
                tau)

    def _extend_final_os_schedule_block(self, schedule):
        """Extends the stop_usec of the final TxOps scheduled to communicate in the
           conservative schedule blocks.

        :param Schedule schedule: The schedule to modify
        """
        num_txops = len(schedule.txops)
        schedule.txops.sort(key=lambda x: x.start_usec)

        for i in range(1, num_txops):
            prev_txop = schedule.txops[i - 1]
            curr_txop = schedule.txops[i]
            communication_gap = curr_txop.start_usec - prev_txop.stop_usec

            if communication_gap > self.constraints_object.guard_band:
                prev_txop.stop_usec += communication_gap - self.constraints_object.guard_band

            elif i == num_txops - 1:
                curr_txop.stop_usec = timedelta(microseconds=99000)

    def _initialize_queue(
            self,
            channel,
            ta_list,
            start_times,
            min_latency,
            deadline_window):
        """
        Constructs the initial queue passed into the scheduling algorithm which contains only the TAs scheduled on the particular channel

        :param Channel channel: The channel to schedule this TA on
        :param [<TA>] ta_list: The list of TAs scheduled on this channel
        :param [<TA>, <time>] start_times: Dictionary containing the start time for each TA. i.e. First time it speaks in the 20ms block.
        :param timedelta min_latency: Minimum latency on this channel
        :return [SchedulingJob] queue: A list of SchedulingJob objects
        """
        queue = []
        for ta in ta_list:
            # Schedule job up
            up_start_deadline = ta.latency + start_times[ta.id_ + 'up']
            curr_job = SchedulingJob(
                ta=ta,
                job_length=ta.compute_communication_length(channel_capacity=channel.capacity, latency=ta.latency) / 2,
                start_deadline=up_start_deadline,
                release_date=min_latency,
                direction="up")
            job = self._deconflict_start_deadlines(
                queue, curr_job, min_latency, deadline_window)
            queue.append(job)

            # Schedule job down
            down_start_deadline = ta.latency + start_times[ta.id_ + 'down']
            curr_job = SchedulingJob(
                ta=ta,
                job_length=ta.compute_communication_length(channel_capacity=channel.capacity, latency=ta.latency) / 2,
                start_deadline=down_start_deadline,
                release_date=min_latency,
                direction="down")
            job = self._deconflict_start_deadlines(
                queue, curr_job, min_latency, deadline_window)
            queue.append(job)

        # Need to sort jobs by earliest start_deadline first
        queue.sort(key=lambda job: job.start_deadline)
        return queue

    def _add_txop_to_schedule(
            self,
            scheduling_job,
            schedule,
            timer,
            tau):
        """Updates the TxOp list to be

        :param SchedulingJob scheduling_job: The scheduling job to create a TxOp node from
        :param Schedule schedule: The schedule this TxOp should be added to
        :param timedelta timer: The start time of the job
        :param timedelta tau: The end time of the job
        """
        total_transmission_time = timer - tau
        one_way_transmission_time = total_transmission_time - self.constraints_object.guard_band
        txop = TxOp(
            ta=scheduling_job.ta,
            radio_link_id=id_to_mac(
                scheduling_job.ta.id_,
                scheduling_job.direction),
            start_usec=tau,
            stop_usec=tau + one_way_transmission_time,
            center_frequency_hz=scheduling_job.ta.channel.frequency,
            txop_timeout=self.constraints_object.txop_timeout)

        schedule.txops.append(txop)

    def _validate_latency_requirement(self, optimizer_result):
        """Validates that the latency of any TA is not over half the epoch

        :param OptimizerResult optimizer_result: The OptimizerResult to ensure this requirement on
        :raise InvalidLatencyRequirementException:
        """
        for ta in optimizer_result.scheduled_tas:
            if ta.latency > (self.constraints_object.epoch / 2):
                raise InvalidLatencyRequirementException(
                    'The epoch ({0}) relative to the given TAs latency requirement ({1}) is not large enough.'.format(
                        self.constraints_object.epoch.get_microseconds(),
                        ta.latency.get_microseconds()),
                    'HybridScheduler.schedule')


    def _deconflict_start_deadlines(self, queue, curr_job, timer, deadline_window):
        """Ensures that curr_job start_deadline is at least deadline_window away from any job in the queue

        :param [<SchedulingJob>] queue: The list of SchedulingJob objects that still need to be processed
        :param SchedulingJob curr_job: The current SchedulingJob being processed
        :param timedelta timer: The current time
        :param timedelta deadline_window: The amount of time to ensure between every job's start_deadline
        """
        queue.sort(key=lambda job: job.start_deadline, reverse=True)

        for job in queue:
            if curr_job.start_deadline > job.start_deadline - \
                    deadline_window and curr_job.start_deadline < job.start_deadline + deadline_window:
                curr_job.start_deadline = job.start_deadline - deadline_window

        queue.sort(key=lambda job: job.start_deadline)
        return curr_job

    def __str__(self):
        return 'HybridScheduler'
