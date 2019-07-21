"""greedy_schedule.py

Constructs TxOps to add to the schedule based on the minimum latency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from datetime import timedelta
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.processing.algorithms.scheduling.scheduling_algorithm import SchedulingAlgorithm
from cp1.utils.mdl_utils import *


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
        for ta in algorithm_result.scheduled_tas:
            one_way_transmission_length = ta.compute_communication_length(ta.channel.capacity, channel_min_latencies[ta.channel.frequency.value], timedelta(microseconds=0)) / 2
            up_start = ta.channel.start_time
            up_stop = one_way_transmission_length + ta.channel.start_time
            down_start = up_stop + algorithm_result.constraints_object.guard_band
            down_stop = down_start + one_way_transmission_length

            ta.channel.start_time = down_stop + algorithm_result.constraints_object.guard_band

            for x in range(ta.channel.num_partitions):
                partition_offset = x * ta.channel.partition_length
                txop_up = TxOp(
                    ta=ta.id_,
                    radio_link_id=id_to_mac(ta.id_, 'up'),
                    start_usec=partition_offset + up_start,
                    stop_usec=partition_offset + up_stop,
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=algorithm_result.constraints_object.txop_timeout)
                txop_down = TxOp(
                    ta=ta.id_,
                    radio_link_id=id_to_mac(ta.id_, 'down'),
                    start_usec=partition_offset + down_start,
                    stop_usec=partition_offset + down_stop,
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=algorithm_result.constraints_object.txop_timeout)

                txop_list.extend([txop_up, txop_down])
        print_arr = []

        return txop_list

    def __str__(self):
        return 'GreedySchedule'
