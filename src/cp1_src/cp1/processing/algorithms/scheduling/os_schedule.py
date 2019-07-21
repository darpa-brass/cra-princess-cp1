"""os_schedule.py

An Operating Systems Scheduling-like TA scheduler. Works similar to the way OS
software schedules tasks; a priority queue with allowed interruptions.
"""
from datetime import timedelta
from cp1.data_objects.processing.scheduling_job import SchedulingJob
from cp1.data_objects.constants.constants import GUARDBAND_OFFSET, DEADLINE_WINDOW
from cp1.utils.mdl_utils import *

from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
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
        timer = timedelta(microseconds=0)

        queue = self._initialize_queue(algorithm_result)
        for item in queue:
            print(item)

        while timer <= algorithm_result.constraints_object.epoch: # Find min start_deadline job with release_date < timer
            curr_job = None
            for i in range(len(queue)):
                if queue[i].release_date <= timer:
                    curr_job = queue.pop(i)
                    break

            if curr_job == None:
                curr_job = queue.pop(0)

            if curr_job.release_date > timer:
                curr_job.release_date = timer

            tau = timer
            timer = min(tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band, queue[0].start_deadline, algorithm_result.constraints_object.epoch) # How long job runs

            if tau >= algorithm_result.constraints_object.epoch: # Stop if we have another communication
                break

            if timer == queue[0].start_deadline and queue[0].start_deadline != tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band: # Pre-empted
                if timer < curr_job.release_date + curr_job.ta.latency: # End before deadline
                    curr_job.job_length -= (timer - tau - 2 * algorithm_result.constraints_object.guard_band)
                    queue.append(curr_job)
                else:
                    next_job = SchedulingJob(
                    ta = curr_job.ta,
                    job_length = (2 * curr_job.job_length) - (timer + tau + 2 * algorithm_result.constraints_object.guard_band),
                    start_deadline = timer + curr_job.ta.latency,
                    release_date = curr_job.release_date + curr_job.ta.latency)
                    queue.append(next_job)

            else:
                next_job = SchedulingJob(
                    ta=curr_job.ta,
                    job_length=curr_job.ta.bandwidth.value /
                        curr_job.ta.channel.capacity.value *
                        curr_job.ta.latency,
                    start_deadline=timer + curr_job.ta.latency,
                    release_date=curr_job.release_date + curr_job.ta.latency)
                queue.append(next_job)

            self._update_txop_list(algorithm_result.constraints_object, curr_job, txop_list, timer, tau)
            queue.sort(key=lambda job: job.start_deadline, reverse=False)

        return txop_list

    def _update_txop_list(self, constraints_object, scheduling_job, txop_list, timer, tau):
        """Translates a SchedulingJob into a TxOp object

        :param ConstraintsObject constraints_object: The ConstraintsObject this TxOp belongs to
        :param SchedulingJob scheduling_job: The SchedulingJob to create a TxOp from
        :param [<TxOp>] txop_list: The list of TxOp objects this class will ultimately return. Created TxOp will be appended to this
        :param timedelta timer: End of the next communication for scheduling_job
        :param timedelta tau: The beginning of the next communication for scheduling_job
        """
        total_transmission_time = timer - tau
        one_way_transmission_time = total_transmission_time / 2 - constraints_object.guard_band

        txop_up = TxOp(
                    ta = scheduling_job.ta,
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'up'),
                    start_usec=tau + GUARDBAND_OFFSET,
                    stop_usec=tau + one_way_transmission_time,
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

        txop_down = TxOp(
                    ta = scheduling_job.ta,
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'down'),
                    start_usec=tau + one_way_transmission_time + constraints_object.guard_band + GUARDBAND_OFFSET,
                    stop_usec=timer - constraints_object.guard_band,
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)
        txop_list.extend([txop_up, txop_down])

    def _initialize_queue(self, algorithm_result):
        """
        Constructs the initial queue passed into the scheduling algorithm.

        :return [SchedulingJob] queue: A list of SchedulingJob objects sorted by min start_dealine first
        """
        queue = []
        for ta in algorithm_result.scheduled_tas:

            # Make sure that the start_deadline is not over the
            # DEADLINE_WINDOW.
            # Only for jobs whose release date is less than or equal to T.
            start_deadline = ta.latency
            for job in queue:
                if job.start_deadline == start_deadline:
                    start_deadline =start_deadline - DEADLINE_WINDOW

            queue.append(
                SchedulingJob(
                    ta=ta,
                    job_length=ta.bandwidth.value / ta.channel.capacity.value *
                    ta.latency,
                    start_deadline=start_deadline,
                    release_date=timedelta(microseconds=0)))

        queue.sort(key=lambda job: job.start_deadline, reverse=False)
        return queue

    def __str__(self):
        return 'OSSchedule'


# from cp1.data_objects.processing.algorithm_result import AlgorithmResult
# from cp1.data_objects.mdl.kbps import Kbps
# from cp1.data_objects.processing.ta import TA
# from cp1.data_objects.processing.channel import Channel
# from cp1.data_objects.processing.constraints_object import ConstraintsObject
#
#
# channel = Channel()
# ta1 = TA(id_='TA1', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=timedelta(microseconds=50000), scaling_factor=1, c=0.005, channel=channel)
# ta2 = TA(id_='TA2', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=timedelta(microseconds=50000), scaling_factor=1, c=0.005, channel=channel)
# ta3 = TA(id_='TA3', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=timedelta(microseconds=20000), scaling_factor=1, c=0.005, channel=channel)
# candidate_tas = [ta1, ta2, ta3]
#
# constraints_object = ConstraintsObject(seed = 1, id_='C1', candidate_tas=candidate_tas, channels=[channel], epoch=timedelta(microseconds=100000))
# algorithm_result = AlgorithmResult(constraints_object = constraints_object, scheduled_tas=candidate_tas, run_time=0.5, solve_time=0.5, value=1000)
#
# os_schedule = OSSchedule()
# new_schedule = os_schedule.schedule(algorithm_result)
#
# print_arr = []
#
# for txop in new_schedule:
#     print_arr.append(txop.start_usec.microseconds)
#     print_arr.append(txop.stop_usec.microseconds)
# print_arr.sort()
# for item in print_arr:
#     print(item)
