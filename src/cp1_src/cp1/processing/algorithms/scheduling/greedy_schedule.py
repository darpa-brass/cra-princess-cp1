"""greedy_schedule.py

Constructs TxOps to add to the schedule based on the minimum latency.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.processing.algorithms.scheduling.scheduling_algorithm import SchedulingAlgorithm
from cp1.utils.mdl_utils import *


class GreedySchedule(SchedulingAlgorithm):
    def schedule(self, algorithm_result, constraints_object):
        txop_list = []

        # Compute the minimum latency TA in each channel
        channel_min_latencies = {}
        for ta in algorithm_result.scheduled_tas:
            if ta.channel.frequency.value in channel_min_latencies:
                min_latency = min(channel_min_latencies[ta.channel.frequency.value], ta.latency.value)
            else:
                min_latency = ta.latency.value
            ta.channel.num_partitions = int(constraints_object.epoch.value / min_latency)
            ta.channel.partition_length = min_latency
            channel_min_latencies[ta.channel.frequency.value] = min_latency

        # Compute the number of partitions and length of each partition on a channel

        # Reassign channel to tas in case it has been removed by an algorithm
        # for ta in txop_schedule:
        #     for channel in constraints_object.channels:
        #         if ta.channel.frequency.value == channel.frequency.value:
        #             ta.channel = channel
        #             break

        # Construct a TxOp node based on the partition length
        for ta in algorithm_result.scheduled_tas:
            one_way_transmission_length = ta.compute_communication_length(ta.channel.capacity, channel_min_latencies[ta.channel.frequency.value], Milliseconds(0)) / 2

            up_start = ta.channel.start_time
            up_stop = one_way_transmission_length + ta.channel.start_time
            down_start = up_stop + constraints_object.guard_band.value
            down_stop = down_start + one_way_transmission_length

            ta.channel.start_time = down_stop + constraints_object.guard_band.value
            for x in range(ta.channel.num_partitions):
                partition_offset = x * ta.channel.partition_length
                txop_up = TxOp(
                    radio_link_id=id_to_mac(ta.id_, 'up'),
                    start_usec=Microseconds(
                        (partition_offset + up_start) * 1000),
                    stop_usec=Microseconds(
                        (partition_offset + up_stop) * 1000),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)
                txop_down = TxOp(
                    radio_link_id=id_to_mac(ta.id_, 'down'),
                    start_usec=Microseconds(
                        (partition_offset + down_start) * 1000),
                    stop_usec=Microseconds(
                        (partition_offset + down_stop) * 1000),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=constraints_object.txop_timeout)

                txop_list.extend([txop_up, txop_down])
        return txop_list
