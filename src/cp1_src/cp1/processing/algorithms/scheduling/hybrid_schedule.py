import time
from datetime import timedelta
from collections import defaultdict
from cp1.common.exception_class import InvalidLatencyRequirementException
from cp1.utils.file_utils.mdl_utils import *
from cp1.processing.algorithms.scheduling.scheduling_algorithm import SchedulingAlgorithm
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.constants.constants import *
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.processing.scheduling_job import SchedulingJob
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.schedule import Schedule


class HybridSchedule(SchedulingAlgorithm):
    def schedule(self, algorithm_result):
        txop_list = []

        # Find the minimum latency TA in each channel
        channel_min_latencies = {}
        for ta in algorithm_result.scheduled_tas:
            if ta.channel.frequency.value in channel_min_latencies:
                min_latency = min(
                    channel_min_latencies[ta.channel.frequency.value], ta.latency)
            else:
                min_latency = ta.latency
            channel_min_latencies[ta.channel.frequency.value] = min_latency

        # Reassign channel to tas in case it has been removed by an algorithm
        for ta in algorithm_result.scheduled_tas:
            for channel in algorithm_result.constraints_object.channels:
                if ta.channel.frequency.value == channel.frequency.value:
                    ta.channel = channel
                    ta.channel.num_partitions = int(
                        algorithm_result.constraints_object.epoch / channel_min_latencies[ta.channel.frequency.value])
                    ta.channel.partition_length = channel_min_latencies[ta.channel.frequency.value]
                    break

        # Construct a TxOp node based on the partition length
        ta_start_times = {}

        # Construct a dictionary mapping each channel to a TA
        channel_to_tas = defaultdict(list)
        for ta in algorithm_result.scheduled_tas:
            channel_to_tas[ta.channel.frequency.value].append(ta)

        for channel, scheduled_tas in channel_to_tas.items():
            for x in range(len(scheduled_tas)):
                ta = algorithm_result.scheduled_tas[x]
                if ta.latency > (algorithm_result.constraints_object.epoch / 2):
                    raise InvalidLatencyRequirementException(
                        'The epoch ({0}) relative to the given TAs latency requirement ({1}) is not large enough.'.format(
                            algorithm_result.constraints_object.epoch.microseconds,
                            ta.latency.microseconds),
                        'HybridSchedule.schedule')

                up_start = ta.channel.start_time
                one_way_transmission_length = ta.compute_communication_length(
                    ta.channel.capacity, channel_min_latencies[ta.channel.frequency.value], timedelta(microseconds=0)) / 2
                if x == len(scheduled_tas) - 1:
                    one_way_transmission_length = (
                        (channel_min_latencies[ta.channel.frequency.value] - up_start) / 2) - algorithm_result.constraints_object.guard_band

                up_stop = one_way_transmission_length + ta.channel.start_time
                down_start = up_stop + algorithm_result.constraints_object.guard_band
                down_stop = down_start + one_way_transmission_length

                ta.channel.start_time = down_stop + algorithm_result.constraints_object.guard_band
                ta_start_times[ta.id_ + 'up'] = up_stop
                ta_start_times[ta.id_ + 'down'] = down_stop
                print(
                    'upstart: {0}, upstop: {1}, downstart: {2}, downstop: {3}, TA: {4}, Channel: {5}'.format(
                        up_start,
                        up_stop,
                        down_start,
                        down_stop,
                        ta.id_,
                        ta.channel.frequency.value))

                for x in [timedelta(microseconds=0), algorithm_result.constraints_object.epoch -
                          channel_min_latencies[ta.channel.frequency.value]]:
                    txop_up = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'up'),
                        start_usec=up_start + x,
                        stop_usec=up_stop + x,
                        center_frequency_hz=ta.channel.frequency,
                        txop_timeout=algorithm_result.constraints_object.txop_timeout)
                    txop_down = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'down'),
                        start_usec=down_start + x,
                        stop_usec=down_stop + x,
                        center_frequency_hz=ta.channel.frequency,
                        txop_timeout=algorithm_result.constraints_object.txop_timeout)
                    txop_list.extend([txop_up, txop_down])

        for channel in algorithm_result.constraints_object.channels:
            # If the channel has a minimum latency of half the epoch
            if 2 * channel_min_latencies[channel.frequency.value] >= algorithm_result.constraints_object.epoch - algorithm_result.constraints_object.guard_band - MDL_MIN_INTERVAL:
                continue

            queue = self._initialize_queue(
                algorithm_result,
                ta_start_times,
                channel_min_latencies,
                channel)
            timer = channel_min_latencies[channel.frequency.value]
            while timer <= algorithm_result.constraints_object.epoch - \
                    channel_min_latencies[channel.frequency.value]:
                for job in queue:
                    print(
                        'queue status: TA {0}, Direction: {1}, Start_Deadline: {2}, joblength: {3}, Release date {4}'.format(
                            job.ta.id_,
                            job.direction,
                            job.start_deadline,
                            job.job_length,
                            job.release_date))

               # Find the smallest start_deadline job with a release date less
               # than the timer
                curr_job = None
                if curr_job is None:
                    curr_job = queue.pop(0)

                if curr_job.release_date > timer:
                    curr_job.release_date = timer

                print(
                    'job scheduled: {0}, {1}'.format(
                        curr_job.ta.id_,
                        curr_job.direction))
                # Figure out how long this job should run for
                tau = timer
                if len(queue) == 0:
                    break

                timer = min(tau + curr_job.job_length + algorithm_result.constraints_object.guard_band,
                            queue[0].start_deadline,
                            algorithm_result.constraints_object.epoch - channel_min_latencies[channel.frequency.value])

                if (timer == algorithm_result.constraints_object.epoch - channel_min_latencies[channel.frequency.value]) and (
                        tau == algorithm_result.constraints_object.epoch - channel_min_latencies[channel.frequency.value]):
                    break
                print(
                    'tau: {0}, timer: {1}, transmission time: {2}'.format(
                        tau, timer, timer - tau))
                print(
                    'Next job: {0} {1}, start_deadline: {2}'.format(
                        queue[0].ta.id_,
                        queue[0].direction,
                        queue[0].start_deadline))
                # This is if this current job gets pre-empted
                job_to_append = None
                if timer == queue[0].start_deadline and queue[0].start_deadline != tau + \
                        curr_job.job_length + algorithm_result.constraints_object.guard_band:  # Pre-empted
                    next_job = SchedulingJob(
                        ta=curr_job.ta,
                        job_length=(
                            2 * curr_job.job_length) - (
                            timer - tau - algorithm_result.constraints_object.guard_band),
                        start_deadline=timer + curr_job.ta.latency,
                        release_date=curr_job.release_date + curr_job.ta.latency,
                        direction=curr_job.direction)
                    job_to_append = next_job

                else:
                    next_job = SchedulingJob(
                        ta=curr_job.ta,
                        job_length=(
                            (curr_job.ta.bandwidth.value /
                             curr_job.ta.channel.capacity.value) *
                            curr_job.ta.latency /
                            2),
                        start_deadline=timer +
                        curr_job.ta.latency,
                        release_date=curr_job.release_date +
                        curr_job.ta.latency,
                        direction=curr_job.direction)
                    job_to_append = next_job
                    print(
                        'TA Job {0}, release date {1}, start_deadline {2}, job_length {3}'.format(
                            next_job.ta.id_,
                            next_job.release_date,
                            next_job.start_deadline,
                            next_job.job_length))

                # if job_to_append.start_deadline >= ta_start_times[job_to_append.ta.id_ + job_to_append.direction] + algorithm_result.constraints_object.epoch  - channel_min_latencies[ta.channel.frequency.value]:
                #     continue
                if job_to_append.start_deadline > algorithm_result.constraints_object.epoch - \
                        channel_min_latencies[ta.channel.frequency.value]:
                    job_to_append.start_deadline = algorithm_result.constraints_object.epoch - \
                        channel_min_latencies[ta.channel.frequency.value]
                    self.deconflict_start_deadlines(
                        queue, job_to_append, timer)
                    # queue.append(job_to_append)
                else:
                    self.deconflict_start_deadlines(
                        queue, job_to_append, timer)
                    # queue.append(job_to_append)
                if job_to_append.start_deadline >= timer + DEADLINE_WINDOW:
                    queue.append(job_to_append)
                self._update_txop_list(
                    algorithm_result.constraints_object,
                    curr_job,
                    txop_list,
                    timer,
                    tau)
                queue.sort(key=lambda job: job.start_deadline, reverse=False)
                print('\n')

        schedules = []
        channel_to_txop = defaultdict(list)
        for txop in txop_list:
            channel_to_txop[txop.ta.channel.frequency.value].append(txop)
        for channel in channel_to_txop:
            schedules.append(Schedule(channel_frequency=channel, txop_list=channel_to_txop[channel]))

        return schedules

    def _initialize_queue(
            self,
            algorithm_result,
            ta_start_times,
            channel_min_latencies,
            channel):
        """
        Constructs the initial queue passed into the scheduling algorithm which contains only the TAs scheduled on the particular channel

        :param [<TA>, <time>] ta_start_times: Dictionary containing the start time for each TA. i.e. First time it speaks in the 20ms block.
        :param [<Frequency>, <time>] channel_min_latencies: Dictionary containing each minimum latency per frequency
        :return [SchedulingJob] queue: A list of SchedulingJob objects
        """
        queue = []
        for ta in algorithm_result.scheduled_tas:

            # Make sure that the start_deadline is not over the
            # DEADLINE_WINDOW.
            # Only for jobs whose release date is less than or equal to T.
            # need one job for up communication
            if ta.channel == channel:
                up_start_deadline = ta.latency + \
                    ta_start_times[ta.id_ + 'up']  # TODO Should be end time
                print('TA latency: {0}, TA start time {1}, TA Up_start_deadline {2}'.format(
                    ta.latency, ta_start_times[ta.id_ + 'up'], up_start_deadline))
                curr_job = SchedulingJob(
                    ta=ta,
                    job_length=(
                        ta.bandwidth.value /
                        ta.channel.capacity.value) *
                    ta.latency / 2,
                    start_deadline=up_start_deadline,
                    release_date=channel_min_latencies[ta.channel.frequency.value],
                    direction="up")
                job = self.deconflict_start_deadlines(
                    queue, curr_job, channel_min_latencies[channel.frequency.value])
                queue.append(job)
                # need one job for down communication
                down_start_deadline = ta.latency + \
                    ta_start_times[ta.id_ + 'down']  # TODO Should be end time
                print('TA latency: {0}, TA start time {1}, TA Down_start_deadline {2}'.format(
                    ta.latency, ta_start_times[ta.id_ + 'down'], down_start_deadline))
                curr_job = SchedulingJob(
                    ta=ta,
                    job_length=(
                        ta.bandwidth.value /
                        ta.channel.capacity.value) *
                    ta.latency / 2,
                    start_deadline=down_start_deadline,
                    release_date=channel_min_latencies[ta.channel.frequency.value],
                    direction="down")
                job = self.deconflict_start_deadlines(
                    queue, curr_job, channel_min_latencies[channel.frequency.value])
                queue.append(job)
        queue.sort(key=lambda job: job.start_deadline, reverse=False)
        return queue

    def _update_txop_list(
            self,
            constraints_object,
            scheduling_job,
            txop_list,
            timer,
            tau):
        total_transmission_time = timer - tau
        one_way_transmission_time = total_transmission_time - constraints_object.guard_band
        print('one_wayt{0}'.format(one_way_transmission_time))
        print('timer{0}'.format(timer))
        print('tau{0}'.format(tau))
        # print("ta{0}, {1} start {2}, stop {3}".format(scheduling_job.ta.id_, scheduling_job.direction, timedelta(microseconds=int(tau + timedelta(microseconds=1))).microseconds, timedelta(microseconds=int(tau + one_way_transmission_time)).microseconds))
        txop = TxOp(
            ta=scheduling_job.ta.id_,
            radio_link_id=id_to_mac(
                scheduling_job.ta.id_,
                scheduling_job.direction),
            start_usec=tau + GUARDBAND_OFFSET,
            stop_usec=tau + one_way_transmission_time,
            center_frequency_hz=scheduling_job.ta.channel.frequency,
            txop_timeout=constraints_object.txop_timeout)

        txop_list.extend([txop])

    def __str__(self):
        return 'HybridSchedule'


# channel1 = Channel(capacity=Kbps(10000))
# #channel2 = Channel(frequency=Frequency(4919600000), capacity = Kbps(100))
# ta1 = TA(
#     id_='TA1',
#     bandwidth=Kbps(50),
#     minimum_voice_bandwidth=Kbps(25),
#     minimum_safety_bandwidth=Kbps(25),
#     latency=timedelta(
#         microseconds=20000),
#     scaling_factor=1,
#     c=0.005,
#     channel=channel1,
#     eligible_channels=[channel1])
# ta2 = TA(
#     id_='TA2',
#     bandwidth=Kbps(3000),
#     minimum_voice_bandwidth=Kbps(1500),
#     minimum_safety_bandwidth=Kbps(1500),
#     latency=timedelta(
#         microseconds=20000),
#     scaling_factor=1,
#     c=0.005,
#     channel=channel1,
#     eligible_channels=[channel1])
# ta3 = TA(
#     id_='TA3',
#     bandwidth=Kbps(3000),
#     minimum_voice_bandwidth=Kbps(1500),
#     minimum_safety_bandwidth=Kbps(1500),
#     latency=timedelta(
#         microseconds=20000),
#     scaling_factor=1,
#     c=0.005,
#     channel=channel1,
#     eligible_channels=[channel1])
#ta4 = TA(id_='TA4', bandwidth=Kbps(70), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=timedelta(microseconds=DEADLINE_WINDOW0), scaling_factor=1, c=0.005, channel=channel2, eligible_channels=[channel1, channel2])

# candidate_tas = [ta1, ta2]#, ta3]
#
# constraints_object = ConstraintsObject(
#     seed=0,
#     id_='C1',
#     candidate_tas=candidate_tas,
#     channels=[channel1],
#     epoch=timedelta(
#         microseconds=100000))

# for ta in candidate_tas:
#     print(ta)
#
# for ta in candidate_tas:
#     time_from_minimum_discretization = timedelta(microseconds=(((ta.bandwidth.value / ta.channel.capacity.value) * ta.latency.microseconds) %  500))
#     if time_from_minimum_discretization > timedelta(microseconds=0):
#         additional_bandwidth_required = ta.compute_bandwidth_requirement(ta.channel.capacity, ta.latency, time_from_minimum_discretization)
#         ta.bandwidth += additional_bandwidth_required
#
# ta1.compute_communication_length()
# for ta in candidate_tas:
#     print(ta)
# from cp1.processing.algorithms.optimization.greedy_optimization import GreedyOptimization
# from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
#
# for ta in constraints_object.candidate_tas:
#     print(ta)
# disc = BandwidthDiscretization(1)
# cbc = GreedyOptimization(constraints_object)
# algorithm_result = cbc.optimize(disc)
#
# for ta in algorithm_result.scheduled_tas:
#     print(ta)
# #
# algorithm_result = AlgorithmResult(
#     constraints_object=constraints_object,
#     scheduled_tas=candidate_tas,
#     run_time=0.5,
#     solve_time=0.5,
#     value=1000)
#
# hybrid_schedule = HybridScheduler()
# new_schedule = hybrid_schedule.schedule(algorithm_result=algorithm_result)
#
# print_arr = []
# new_schedule.sort(key=lambda x: x.start_usec, reverse=False)
# for txop in new_schedule:
#     print(txop.ta, txop.start_usec.microseconds, txop.stop_usec.microseconds)
# for txop in new_schedule:
#     print_arr.append(txop.start_usec.microseconds)
#     print_arr.append(txop.stop_usec.microseconds)
# print_arr.sort()
# for item in print_arr:
#     print(item)
