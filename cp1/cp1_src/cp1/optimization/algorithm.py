"""

optimization_algorithm.py

Optimizes schedule based on constraints and channel bandwidth.

Author: Tameem Samawi (tsamawi@cra.com)

"""
from cra.mdl_data.mdl_txop import MDLTxOp
from cra.mdl_data.mdl_schedule import MDLSchedule


def optimize(constraints_object):
    """
    Creates a new schedule based on updated bandwidth availability, channel frequency and TAs seeking to join the
    network

    :param constraints_object: The set of constraints on the schedule including the list of candidate TAs,
                               available frequencies and new amount of available bandwidth
    :param constraints_object: ConstraintsObject

    :returns schedules: Dictionary containing a new schedule for each channel
    """
    schedule = MDLSchedule(
        constraints_object.epoch,
        constraints_object.guard_band)

    channel = constraints_object.channel
    first_available_time = 0
    num_partitions = 5
    channel_length = channel.capacity.value / num_partitions

    # Sort channel in decreasing order according to value
    constraints_object.candidate_tas.sort(
        key=lambda ta: ta.utility_threshold, reverse=True)

    for ta in constraints_object.candidate_tas:
        two_way_transmission_length = ta.total_minimum_bandwidth.value / channel_length
        one_way_transmission_length = two_way_transmission_length / 2
        two_way_communication_guard_band = 2 * constraints_object.guard_band.toSeconds()
        remaining_time = channel_length - first_available_time

        if two_way_transmission_length + two_way_communication_guard_band <= remaining_time:
            # Create new TxOp node
            transmission_1_start = first_available_time
            transmission_1_stop = one_way_transmission_length + first_available_time

            transmission_2_start = transmission_1_stop + constraints_object.guard_band
            transmission_2_stop = one_way_transmission_length + transmission_1_stop

            txop_down = MDLTxOp(
                start_usec=transmission_1_start,
                stop_usec=transmission_1_stop,
                center_frequency_hz=constraints_object.channel.frequency,
                txop_timeout=constraints_object.channel.timeout
            )
            txop_up = MDLTxOp(
                start_usec=transmission_2_start,
                stop_usec=transmission_2_stop,
                center_frequency_hz=constraints_object.channel.frequency,
                txop_timeout=constraints_object.channel.timeout)

            schedule.add(ta.id_, txop_up)
            schedule.add(ta.id_, txop_down)

            first_available_time += transmission_2_stop + constraints_object.guard_band

    return schedule
