"""

bandwidth.py

Generates a dictionary of bandwidth keys based on TAs and bandwidth availability.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.schedule import Schedule
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.kbps import Kbps
import os
import json


def process_bandwidth(constraints_object, bandwidth_file):
    """
    Creates a dictionary of bandwidth keys/values based on TAs

    :param constraints_object: The set of constraints on the schedule including the list of candidate TAs,
                               available frequencies and new amount of available bandwidth
    :param constraints_object: ConstraintsObject

    :returns schedule: Dictionary containing a list of new bandwidth values.
    """
    data_file= open(bandwidth_file, 'r')
    configMap = json.load(data_file)

    ground_from = configMap['Ground']['from']
    ground_to = configMap['Ground']['to']
    voice = configMap['ServiceLevelProfiles']['voice']
    safety = configMap['ServiceLevelProfiles']['safety']
    bulk = configMap['ServiceLevelProfiles']['bulk']

    data_file.close()

    new_rates = []
    for ta in constraints_object.candidate_tas:
        voice_slp_id_up = ground_from + '_to_' + ta.id_.value + '_' + voice
        voice_slp_id_down = ta.id_.value + '_to_' + ground_to + '_' + voice

        safety_slp_id_up = ground_from + '_to_' + ta.id_.value + '_' + safety
        safety_slp_id_down = ta.id_.value + '_to_' + ground_to + '_' + safety

        bulk_slp_id_up = ground_from + '_to_' + ta.id_.value + '_' + bulk
        bulk_slp_id_down = ta.id_.value + '_to_' + ground_to + '_' + bulk

        up_ratio = 0.5
        down_ratio = 0.5
        new_rates.append((voice_slp_id_up, int(constraints_object.goal_throughput_voice.rate.to_bits_per_second() * up_ratio)))
        new_rates.append((voice_slp_id_down, int(constraints_object.goal_throughput_voice.rate.to_bits_per_second() * down_ratio)))

        new_rates.append((safety_slp_id_up, int(constraints_object.goal_throughput_safety.rate.to_bits_per_second() * up_ratio)))
        new_rates.append((safety_slp_id_down, int(constraints_object.goal_throughput_safety.rate.to_bits_per_second() * down_ratio)))

        new_rates.append((bulk_slp_id_up, int(constraints_object.goal_throughput_bulk.rate.to_bits_per_second() * up_ratio)))
        new_rates.append((bulk_slp_id_down, int(constraints_object.goal_throughput_bulk.rate.to_bits_per_second() * down_ratio)))

    return new_rates
