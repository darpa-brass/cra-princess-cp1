"""

algorithm.py

Optimizes schedule based on constraints and channel bandwidth.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.schedule import Schedule
from cp1.data_objects.mdl.microseconds import Microseconds


def optimize(constraints_object):
    """
    Creates a new schedule based on updated bandwidth availability, channel frequency and TAs seeking to join the
    network

    :param constraints_object: The set of constraints on the schedule including the list of candidate TAs,
                               available frequencies and new amount of available bandwidth
    :param constraints_object: ConstraintsObject

    :returns schedule: Dictionary containing a new schedule for each channel
    """
    schedule = Schedule(
        constraints_object.epoch,
        constraints_object.guard_band)

    guard_band = constraints_object.guard_band.value
    channel = constraints_object.channel

    if constraints_object.latency.value == 0:
        num_partitions = 1
    else:
        num_partitions = (channel.capacity.value / constraints_object.latency.value)

    channel_length = channel.capacity.value / num_partitions
    # Sort channel in decreasing order according to value
    constraints_object.candidate_tas.sort(
        key=lambda ta: ta.utility_threshold, reverse=True)

    first_available_time = 0
    for ta in constraints_object.candidate_tas:
        two_way_transmission_length = (ta.total_minimum_bandwidth.value / channel.capacity.value) * channel_length
        one_way_transmission_length = two_way_transmission_length / 2
        two_way_communication_guard_band = 2 * guard_band
        remaining_time = channel_length - first_available_time

        if two_way_transmission_length + two_way_communication_guard_band <= remaining_time:
            # Create new TxOp node
            transmission_up_start = first_available_time
            transmission_up_stop = one_way_transmission_length + first_available_time

            transmission_down_start = transmission_up_stop + guard_band
            transmission_down_stop = one_way_transmission_length + transmission_up_stop

            radio_link_up_key = 'GR1_to_' + ta.id_.value
            radio_link_down_key = ta.id_.value + '_to_GR1'

            for x in range(num_partitions - 1):
                offset = x * channel_length
                txop_down = TxOp(
                    start_usec=Microseconds((offset + transmission_up_start) * 1000),
                    stop_usec=Microseconds((offset + transmission_up_stop) * 1000),
                    center_frequency_hz=constraints_object.channel.frequency,
                    txop_timeout=constraints_object.channel.timeout
                )
                txop_up = TxOp(
                    start_usec=Microseconds((offset + transmission_down_start) * 1000),
                    stop_usec=Microseconds((offset + transmission_down_stop) * 1000),
                    center_frequency_hz=constraints_object.channel.frequency,
                    txop_timeout=constraints_object.channel.timeout)

                schedule.add(radio_link_down_key, txop_down)
                schedule.add(radio_link_up_key, txop_up)

            first_available_time += transmission_down_stop + guard_band

    return schedule
