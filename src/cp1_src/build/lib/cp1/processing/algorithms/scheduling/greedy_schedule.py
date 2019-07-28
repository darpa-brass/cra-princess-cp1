"""greedy_schedule.py

Constructs TxOps to add to the schedule based on the minimum latency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from datetime import timedelta
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.schedule import Schedule
from cp1.processing.algorithms.scheduling.scheduling_algorithm import SchedulingAlgorithm
from cp1.utils.file_utils.mdl_utils import *
from collections import defaultdict


class GreedySchedule(SchedulingAlgorithm):
    def schedule(self, algorithm_result):
        txop_list = []

        # Find the minimum latency TA in each channel
        channel_min_latencies = {}
        for ta in algorithm_result.scheduled_tas:
            if ta.channel.frequency.value in channel_min_latencies:
                min_latency = min(channel_min_latencies[ta.channel.frequency.value], ta.latency)
            else:
                min_latency = ta.latency
            channel_min_latencies[ta.channel.frequency.value] = min_latency

        # Reassign channel to tas in case it has been removed by an algorithm
        for ta in algorithm_result.scheduled_tas:
            for channel in algorithm_result.constraints_object.channels:
                if ta.channel.frequency.value == channel.frequency.value:
                    ta.channel = channel
                    ta.channel.num_partitions = int(algorithm_result.constraints_object.epoch / channel_min_latencies[ta.channel.frequency.value])
                    ta.channel.partition_length = channel_min_latencies[ta.channel.frequency.value]
                    break

        # Construct a TxOp node based on the partition length
        # Construct a dictionary mapping each channel to a TA
        channel_to_tas = defaultdict(list)
        for ta in algorithm_result.scheduled_tas:
            channel_to_tas[ta.channel.frequency.value].append(ta)

        for channel, scheduled_tas in channel_to_tas.items():
            for x in range(len(scheduled_tas)):
                ta = algorithm_result.scheduled_tas[x]
                one_way_transmission_length = ta.compute_communication_length(ta.channel.capacity, channel_min_latencies[ta.channel.frequency.value], timedelta(microseconds=0)) / 2
                up_start = ta.channel.start_time

                if x == len(scheduled_tas) - 1:
                    one_way_transmission_length = (
                    (channel_min_latencies[ta.channel.frequency.value] - up_start) / 2) - algorithm_result.constraints_object.guard_band

                up_stop = one_way_transmission_length + ta.channel.start_time
                down_start = up_stop + algorithm_result.constraints_object.guard_band
                down_stop = down_start + one_way_transmission_length

                ta.channel.start_time = down_stop + algorithm_result.constraints_object.guard_band
                for x in range(ta.channel.num_partitions):
                    partition_offset = x * ta.channel.partition_length
                    txop_up = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'up'),
                        start_usec=partition_offset + up_start,
                        stop_usec=partition_offset + up_stop,
                        center_frequency_hz=ta.channel.frequency,
                        txop_timeout=algorithm_result.constraints_object.txop_timeout)
                    txop_down = TxOp(
                        ta=ta,
                        radio_link_id=id_to_mac(ta.id_, 'down'),
                        start_usec=partition_offset + down_start,
                        stop_usec=partition_offset + down_stop,
                        center_frequency_hz=ta.channel.frequency,
                        txop_timeout=algorithm_result.constraints_object.txop_timeout)

                    txop_list.extend([txop_up, txop_down])
        print_arr = []

        schedules = []
        channel_to_txop = defaultdict(list)
        for txop in txop_list:
            channel_to_txop[txop.ta.channel.frequency.value].append(txop)
        for channel in channel_to_txop:
            schedules.append(Schedule(channel_frequency=channel, txop_list=channel_to_txop[channel]))

        return schedules

    def __str__(self):
        return 'GreedySchedule'
