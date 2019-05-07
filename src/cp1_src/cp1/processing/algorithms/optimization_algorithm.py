"""
optimization_algorithm.py

Interface for algorithms.
"""
import abc
from ortools.linear_solver import pywraplp
from cp1.data_objects.processing.schedule import Schedule


class OptimizationAlgorithm(abc.ABC):
    @abc.abstractmethod
    def __init__(self, constraints_object):
        pass

    @abc.abstractmethod
    def optimize(self):
        pass

    def construct_txop_nodes(self, algorithm_result, epoch, guard_band, txop_timeout):
        schedule = Schedule(epoch, guard_band)

        # Compute the minimum latency TA in each channel
        channel_min_latencies = {}
        for ta in algorithm_result.scheduled_tas:
            if ta.channel.frequency.value in channels:
                channel_min_latencies[channel] = min(channel[channel.frequency.value], ta.latency.value)
            else:
                channel_min_latencies[channel] = ta.latency.value

        # Assign partition length and num_partitions to each channel
        for channel, min_latency in channel_min_latencies:
            channel.num_partitions = epoch / min_latency
            channel.partition_length = min_latency

        # Construct a TxOp node based on the partition length
        for ta in algorithm_result.scheduled_tas:
            one_way_transmission_length = ta.compute_communication_length(ta.bandwidth) / ta.channel.num_partitions

            up_start = ta.channel.start_time
            up_stop = one_way_transmission_length + ta.channel.start_time
            down_start = up_stop + guard_band.value
            down_stop = down_start + one_way_transmission_length

            ta.channel.start_time = down_stop + guard_band.value

            up_key = 'GR1_to_' + ta.id_
            down_key = ta.id_ + '_to_GR1'

            for x in range(ta.channel.num_partitions):
                partition_offset = x * ta.channel.partition_length
                txop_up = TxOp(
                    start_usec=Microseconds(
                        (partition_offset + up_start) * 1000),
                    stop_usec=Microseconds(
                        (partition_offset + up_stop) * 1000),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=txop_timeout)
                txop_down = TxOp(
                    start_usec=Microseconds(
                        (partition_offset + down_start) * 1000),
                    stop_usec=Microseconds(
                        (partition_offset + down_stop) * 1000),
                    center_frequency_hz=ta.channel.frequency,
                    txop_timeout=txop_timeout)

                schedule.add(up_key, txop_up)
                schedule.add(down_key, txop_down)
        return schedule
