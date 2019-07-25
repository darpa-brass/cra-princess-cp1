"""os_schedule.py

An Operating Systems Scheduling-like TA scheduler. Works similar to the way OS
software schedules tasks; a priority queue with allowed interruptions.
"""
from cp1.data_objects.processing.scheduling_job import SchedulingJob
from cp1.data_objects.constants.constants import *
from cp1.utils.file_utils.mdl_utils import *
import random


from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.algorithm_result import AlgorithmResult




class OSSchedule:
    def schedule(self, algorithm_result):
        """
        Schedules TAs using an algorithm similar to OS Scheduling algorithms.

        :return [TxOp] txop_list: A list of TxOp objects
        """
        txop_list = []
        timer = 0

        queue = self._initialize_queue(algorithm_result)

        while timer <= algorithm_result.constraints_object.epoch.value:
            for j in queue:
                print(j.ta.id_, j.release_date, j.start_deadline, j.job_length)
            # Find the smallest start_deadline job with a release date less than the timer
            curr_job = None
            for i in range(len(queue)):
                if queue[i].release_date <= timer:
                    curr_job = queue.pop(i)
                    break

            if curr_job == None:
                print('None')
                curr_job = queue.pop(0)

            if curr_job.release_date > timer:
                curr_job.release_date = timer

            # Figure out how long this job should run for
            tau = timer
            timer = min(tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band.value, queue[0].start_deadline)# - (random.uniform(0, 1) * 0.01))

            if timer == queue[0].start_deadline and queue[0].start_deadline != tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band.value: # Somebody pre-empted me
                if timer < curr_job.release_date + curr_job.ta.latency.value: # I ended before my deadline
                    # This job has to be added to the queue.
                    curr_job.job_length -= (timer - tau - 2 * algorithm_result.constraints_object.guard_band.value)
                    queue.append(curr_job)
                else:
                    next_job = SchedulingJob(
                    ta = curr_job.ta,
                    job_length = (2 * curr_job.job_length) - (timer + tau + 2 * algorithm_result.constraints_object.guard_band.value),
                    start_deadline = timer + curr_job.ta.latency.value,
                    release_date = curr_job.release_date + curr_job.ta.latency.value
                    )
                    queue.append(next_job)

            else:
                next_job = SchedulingJob(
                    ta=curr_job.ta,
                    job_length=(
                        (curr_job.ta.bandwidth.value /
                        curr_job.ta.channel.capacity.value) *
                        curr_job.ta.latency.value),
                    start_deadline=timer + curr_job.ta.latency.value,
                    release_date=curr_job.release_date + curr_job.ta.latency.value)
                queue.append(next_job)

            self._update_txop_list(algorithm_result.constraints_object, curr_job, txop_list, timer, tau)
            queue.sort(key=lambda job: job.start_deadline, reverse=False)

        return txop_list

    def _update_txop_list(self, constraints_object, scheduling_job, txop_list, timer, tau):
        # Split between up and down
        total_transmission_time = timer - tau
        one_way_transmission_time = (total_transmission_time / 2) - constraints_object.guard_band.value

        txop_up = TxOp(
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'up'),
                    start_usec=Microseconds((1000 * tau) + 1),
                    stop_usec=Microseconds(1000 * (tau + one_way_transmission_time)),
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

        txop_down = TxOp(
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'down'),
                    start_usec=Microseconds((1000 * (tau + one_way_transmission_time + constraints_object.guard_band.value)) + 1),
                    stop_usec=Microseconds(1000 * (timer - constraints_object.guard_band.value)),
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

        print('Scheduling Job')
        print(txop_up.start_usec.value)
        print(txop_down.stop_usec.value)
        txop_list.extend([txop_up, txop_down])

    def _initialize_queue(self, algorithm_result):
        """
        Constructs the initial queue passed into the scheduling algorithm.

        :return [SchedulingJob] queue: A list of SchedulingJob objects
        """
        queue = []
        for ta in algorithm_result.scheduled_tas:

            # Make sure that the start_deadline is not over the
            # DEADLINE_WINDOW.
            # Only for jobs whose release date is less than or equal to T.
            start_deadline = ta.latency.value
            for job in queue:
                if job.start_deadline == start_deadline:
                    start_deadline -= DEADLINE_WINDOW

            queue.append(
                SchedulingJob(
                    ta=ta,
                    job_length=(
                        ta.bandwidth.value /
                        ta.channel.capacity.value) *
                    ta.latency.value,
                    start_deadline=start_deadline,
                    release_date=0))

        queue.sort(key=lambda job: job.start_deadline, reverse=False)
        return queue

    def __str__(self):
        return 'OS Schedule'
