import time
from datetime import time as time_
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.constants.constants import *
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.processing.scheduling_job import SchedulingJob
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.utils.mdl_utils import *
from cp1.processing.algorithms.scheduling.scheduling_algorithm import SchedulingAlgorithm


class HybridScheduler(SchedulingAlgorithm):
    def deconflict_start_deadlines(self, queue, curr_job):
        for job in queue:
            if curr_job.start_deadline == job.start_deadline:
                curr_job.start_deadline -= DEADLINE_WINDOW
                self.deconflict_start_deadlines(queue, curr_job)
        return curr_job

    def schedule(self, algorithm_result):
        txop_list = []

        # Find the minimum latency TA in each channel
        channel_min_latencies = {}
        for ta in algorithm_result.scheduled_tas:
            if ta.channel.frequency.value in channel_min_latencies:
                min_latency = min(channel_min_latencies[ta.channel.frequency.value], ta.latency.microsecond)
            else:
                min_latency = ta.latency.microsecond
            channel_min_latencies[ta.channel.frequency.value] = min_latency

        # Reassign channel to tas in case it has been removed by an algorithm
        for ta in algorithm_result.scheduled_tas:
            for channel in algorithm_result.constraints_object.channels:
                if ta.channel.frequency.value == channel.frequency.value:
                    ta.channel = channel
                    ta.channel.num_partitions = int(algorithm_result.constraints_object.epoch.microsecond / channel_min_latencies[ta.channel.frequency.value])
                    ta.channel.partition_length = channel_min_latencies[ta.channel.frequency.value]
                    break

        # Construct a TxOp node based on the partition length
        ta_start_times = {}
        for x in range(len(algorithm_result.scheduled_tas)):
            ta = algorithm_result.scheduled_tas[x]

            up_start = ta.channel.start_time
            one_way_transmission_length = ta.compute_communication_length(ta.channel.capacity, channel_min_latencies[ta.channel.frequency.value], time_(microsecond=0)) / 2
            if x == len(algorithm_result.scheduled_tas) - 1:
                one_way_transmission_length = ((20000 - up_start) / 2) - algorithm_result.constraints_object.guard_band.microsecond

            up_stop = one_way_transmission_length + ta.channel.start_time
            down_start = up_stop + algorithm_result.constraints_object.guard_band.microsecond
            down_stop = down_start + one_way_transmission_length

            ta.channel.start_time = down_stop + algorithm_result.constraints_object.guard_band.microsecond
            ta_start_times[ta.id_] = up_start

            for x in [0, 80000]:
                txop_up = TxOp(
                    ta=ta.id_,
                    radio_link_id=id_to_mac(ta.id_, 'up'),
                    start_usec=time_(
                        microsecond=int(up_start + x)),
                    stop_usec=time_(
                        microsecond=int(up_stop + x)),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=algorithm_result.constraints_object.txop_timeout)
                txop_down = TxOp(
                    ta=ta.id_,
                    radio_link_id=id_to_mac(ta.id_, 'down'),
                    start_usec=time_(
                        microsecond=int(down_start + x)),
                    stop_usec=time_(
                        microsecond=int(down_stop + x)),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=algorithm_result.constraints_object.txop_timeout)

                txop_list.extend([txop_up, txop_down])

        queue = self._initialize_queue(algorithm_result, ta_start_times, channel_min_latencies)

        timer = 20000
        while timer <= algorithm_result.constraints_object.epoch.microsecond - 20000: # 20 needs to be changed to the channel's partition length. Also coded for multiple channels.
            # Find the smallest start_deadline job with a release date less than the timer
            curr_job = None
            for i in range(len(queue)):
                if queue[i].release_date <= timer:
                    curr_job = queue.pop(i)
                    break

            if curr_job == None:
                curr_job = queue.pop(0)

            if curr_job.release_date > timer:
                curr_job.release_date = timer

            # Figure out how long this job should run for
            tau = timer
            if len(queue) == 0:
                break
            timer = min(tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band.microsecond, queue[0].start_deadline, 80000)# - (random.uniform(0, 1) * 0.01))
            if timer == 80000 and tau == 80000:
                break

            # This is if this current job gets pre-empted
            job_to_append = None
            if timer == queue[0].start_deadline and queue[0].start_deadline != tau + curr_job.job_length + 2 * algorithm_result.constraints_object.guard_band.microsecond: # Somebody pre-empted me and i wasn't done talking yet
                if timer < curr_job.release_date + curr_job.ta.latency.microsecond: # I ended before my deadline
                    # This job has to be added to the queue.
                    curr_job.job_length -= (timer - tau - 2 * algorithm_result.constraints_object.guard_band.microsecond)
                    job_to_append = curr_job
                else:
                    next_job = SchedulingJob(
                    ta = curr_job.ta,
                    job_length = (2 * curr_job.job_length) - (timer + tau + 2 * algorithm_result.constraints_object.guard_band.microsecond),
                    start_deadline = timer + curr_job.ta.latency.microsecond,
                    release_date = curr_job.release_date + curr_job.ta.latency.microsecond
                    )
                    job_to_append = next_job

            else:
                next_job = SchedulingJob(
                    ta=curr_job.ta,
                    job_length=(
                        (curr_job.ta.bandwidth.value /
                        curr_job.ta.channel.capacity.value) *
                        curr_job.ta.latency.microsecond),
                    start_deadline=timer + curr_job.ta.latency.microsecond,
                    release_date=curr_job.release_date + curr_job.ta.latency.microsecond)
                job_to_append = next_job

            # if job_to_append.start_deadline >= ta_start_times[job_to_append.ta.id_] + 80:
            #     continue
            if job_to_append.start_deadline > 80000:
                self.deconflict_start_deadlines(queue, job_to_append)
                queue.append(job_to_append)
            else:
                queue.append(job_to_append)

            self._update_txop_list(algorithm_result.constraints_object, curr_job, txop_list, timer, tau)
            queue.sort(key=lambda job: job.start_deadline, reverse=False)

        return txop_list

    def _initialize_queue(self, algorithm_result, ta_start_times, channel_min_latencies):
        """
        Constructs the initial queue passed into the scheduling algorithm.

        :param [<TA>, <time>] ta_start_times: Dictionary containing the start time for each TA. i.e. First time it speaks in the 20ms block.
        :param [<Frequency>, <time>] channel_min_latencies: Dictionary containing each minimum latency per frequency
        :return [SchedulingJob] queue: A list of SchedulingJob objects
        """
        queue = []
        for ta in algorithm_result.scheduled_tas:

            # Make sure that the start_deadline is not over the
            # DEADLINE_WINDOW.
            # Only for jobs whose release date is less than or equal to T.
            start_deadline = ta.latency.microsecond + ta_start_times[ta.id_] #TODO Should be end time
            curr_job = SchedulingJob(
                ta=ta,
                job_length=(
                    ta.bandwidth.value /
                    ta.channel.capacity.value) *
                ta.latency.microsecond,
                start_deadline=start_deadline,
                release_date=channel_min_latencies[ta.channel.frequency.value])
            job = self.deconflict_start_deadlines(queue, curr_job)
            queue.append(job)

        queue.sort(key=lambda job: job.start_deadline, reverse=False)
        return queue

    def _update_txop_list(self, constraints_object, scheduling_job, txop_list, timer, tau):
        # Split between up and down
        total_transmission_time = timer - tau
        one_way_transmission_time = (total_transmission_time / 2) - constraints_object.guard_band.microsecond
        txop_up = TxOp(
                    ta=scheduling_job.ta.id_,
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'up'),
                    start_usec=time_(microsecond=int(tau + 1)),
                    stop_usec=time_(microsecond=int(tau + one_way_transmission_time)),
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

        txop_down = TxOp(
                    ta=scheduling_job.ta.id_,
                    radio_link_id=id_to_mac(scheduling_job.ta.id_, 'down'),
                    start_usec=time_(microsecond=int(tau + one_way_transmission_time + constraints_object.guard_band.microsecond + GUARDBAND_OFFSET.microsecond)),
                    stop_usec=time_(microsecond=int(timer - constraints_object.guard_band.microsecond)),
                    center_frequency_hz=scheduling_job.ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

        txop_list.extend([txop_up, txop_down])

    def __str__(self):
        return 'HybridSchedule'
