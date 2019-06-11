"""json_utils.py

Module to hold any JSON utility functions.
Author: Tameem Samawi (tsamawi@cra.com)
"""

import json
#from cp1.common.logger import Logger

logger = Logger().logger

def extract_percentages(field):
    perc = []
    for x in field:
        perc.append(x[0])
    return perc

def file_to_json(file_path):
    """
    Deserializes json object in file into a Python object.

    :param str file_path: Database name.

    :returns json_map: Return type varies based on input, should be dict
    """
    file = open(file_path, 'r')
    json_map = json.load(file)
    file.close()
    return json_map


# def create_mdl_bandwidth_set(mdl_bandwidth_dict):
#     """
#     Constructs a MDLBandwidthSet object from bandwidth_dict. Use with file_to_json.
#
#     :param dict{str: str} mdl_bandwidth_dict: Output from file_to_json
#
#     :returns mdl_bandwidth_set: An MDLBandwidthSet instance constructed from the input.
#     """
#     print('Extracting values from %s', mdl_bandwidth_dict)
#
#     mdl_bandwidth_rates = []
#
#     for type in Constants.mdl_bandwidth_types:
#         radioA_to_radioB_id = mdl_bandwidth_dict[type][Constants.radioA_to_radioB_id_key]
#         radioA_to_radioB_value = mdl_bandwidth_dict[type][Constants.radioA_to_radioB_value_key]
#         radioB_to_radioA_id = mdl_bandwidth_dict[type][Constants.radioB_to_radioA_id_key]
#         radioB_to_radioA_value = mdl_bandwidth_dict[type][Constants.radioB_to_radioA_value_key]
#         mdl_bandwidth_rates.append(MDLBandwidthRate(
#             radioA_to_radioB_id, radioA_to_radioB_value, radioB_to_radioA_id, radioB_to_radioA_value))
#
#     mdl_bandwidth_set = MDLBandwidthSet(
#         mdl_bandwidth_rates[0], mdl_bandwidth_rates[1], mdl_bandwidth_rates[2], mdl_bandwidth_rates[3])
#     return mdl_bandwidth_set
