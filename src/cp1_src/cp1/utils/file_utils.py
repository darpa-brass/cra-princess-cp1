"""file_utils.py

Any helper functions related to parsing MDL files.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import re
import csv
import os
import shutil
from tempfile import NamedTemporaryFile
from collections import defaultdict

from cp1.common.exception_class import MACAddressParseError
from cp1.data_objects.constants.constants import *

from cp1.utils.orientdb_session import OrientDBSession
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.algorithms.discretizers.accuracy_discretizer import AccuracyDiscretizer
from cp1.algorithms.discretizers.bandwidth_discretizer import BandwidthDiscretizer
from cp1.algorithms.discretizers.value_discretizer import ValueDiscretizer


def store_and_retrieve_constraints(constraints_object_list):
    """Performs setup, teardown and calls necessary method to store and retrieve a list of ConstraintsObjects

    :param [<ConstraintsObject>] constraints_object_list: A list of ConstraintsObjects to store in OrientDB
    :returns [<ConstraintsObject>] orientdb_constraints_object_list: The same list of Constraints, as retrieved from OrientDB
    """
    constraints_orientdb = OrientDBSession(
        database_name=CONSTRAINTS_DB,
        config_file=ORIENTDB_CONFIG_FILE)

    constraints_orientdb.open_database()
    orientdb_constraints_object_list = constraints_orientdb.store_and_retrieve_constraints(
        constraints_object_list)
    constraints_orientdb.close_database()
    return orientdb_constraints_object_list


def clear_files(folders):
    """Deletes all files and subfiles found under the folders specified

    :param [<str>] folders: The list of folders to delete
    """
    for folder in folders:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)


def determine_file_name(
        discretizer,
        optimizer,
        scheduler,
        timestamp,
        perturber=None,
        seed=None):
    """Determines the appropriate name for an MDL or RAW output file

    :param Discretizer discretizer: The discretizer used to solve this instance
    :param Optimizer optimizer: The optimizer used to solve this instance
    :param Scheduler scheduler: The scheduler used to solve this instance
    :param str timestamp: The time this was executed
    :param Perturber perturber: The perturber used to perturb this instance
    :param str seed: The seed used to generate this instance

    :returns str file_name: A name for the output file
    """
    file_name = '{0}_{1}_{2}_{3}'.format(
        str(discretizer),
        str(optimizer),
        str(scheduler),
        timestamp)

    if perturber is not None:
        perturber_str = '{0}_{1}_{2}_{3}_{4}_'.format(perturber.reconsider,
                                                    perturber.combine,
                                                    perturber.ta_bandwidth,
                                                    perturber.channel_dropoff,
                                                    perturber.channel_capacity)
        file_name = perturber_str + file_name

    if seed is not None:
        file_name += '_' + str(seed)

    return file_name


def channel_efficiency_print_value(channel_efficiency):
    """Utility function to format how the channel efficiency values should be
       output to a file.

    :param {Channel: int} channel_efficiency: A dictionary of efficiency values
    """
    channel_efficiency_print = ''
    for channel, efficiency in channel_efficiency.items():
        channel_efficiency_print += ('{0},{1},').format(
            channel.frequency.value, efficiency)
    channel_efficiency_print = channel_efficiency_print[:-1]
    return channel_efficiency_print

# def export_perturbed_raw(csv_output, opt_res, upper_opt_res, channel_efficiency):
#     new_rows = []
#     # First export all original rows in the code
#     tempfile = NamedTemporaryFile(delete=False)
#
#     with open(csv_output, 'r') as csvFile, tempfile:
#         reader = csv.reader(csvFile, delimiter=',', quotechar='"')
#         writer = csv.writer(tempfile, delimiter=',', quotechar='"')
#
#         for row in reader:
#             row.append(str(opt_res.value))
#             row.append(str(upper_opt_res.value))
#             row.append(str(opt_res.run_time))
#             row.append(str(opt_res.solve_time))
#             for channel, efficiency in channel_efficiency.items():
#                 row.append(str(channel.frequency.value))
#                 row.append(str(efficiency))
#             print(row)
#             writer.writerow(row)
#
#     shutil.move(tempfile.name, csv_output)


def export_visual(csv_output, opt_res, webserver=False):
    """Exports the data required to visualize

    :param str csv_output: The name of the CSV file to append the data to
    :param OptimizationResult opt_res: The optimization result to export visual
                                       data based off of

    Should be of the format: [ta.id_,
                             cumulative_bandwidth,
                             ta.value,
                             ta.channel_frequency]

    [TA1, 0, 0, 4919500000]
    [TA1, 1, 0, 4919500000] <--- The TA has no value at 1 Kbps
    ...
    [TA1, 45, 24, 4919500000] <--- The minimum bandwidth was 45, and the value
                                   provided at that was 24.
    ...
    [TA1, 158, 56, 4919500000]
    [TA1, 158.2, 56.1, 4919500000] <--- There will be math.floor(ta.bandwidth)
                                        data points for a TA iff (if and only
                                        if) the TA's assigned bandwidth is not a
                                        whole number.
                                        i.e. bw = 158.79 (159 samples)
                                        i.e. bw = 160.0 (160 samples)
    [TA3, 159.2, 56.1, 4919500000] <--- The next value will be the next scheduled
                                        TA
    [TA3, 160.2, 56.1, 4919500000] <--- The value should not increase for the
                                        next entry, this represents TA3 with 2
                                        assigned Kbps, not TA3 with 160.2 bw.
                                        This is just to make frontend work easier.
    [TA3, 285.2, 148.89, 4919500000]
    [TA3, 285.789, 149, 4919500000] <--- TA3 had 127.589 Kbps of bandwidth
                                         assigned to it, so the next value of
                                         the cumulative_bw at the end of TA3 is
                                         158.2 + 127.589 = 285.789
                                         As before, n + 1 data points in this
                                         array belong to TA3.
    """
    visualization_points = defaultdict(list)
    rows = []
    cumulative_bw = 0
    cumulative_val = 0
    for ta in opt_res.scheduled_tas:
        rows.append([ta.id_])
        for bw in range(1, int(ta.bandwidth.value) + 2):

            # If we are at the last index, compute the actual bandwidth.
            # i.e. Bandwidth = 10.48
            #      for i in range(12):
            #      When we get to 11, just calculate bw @ 10.48
            if bw == int(ta.bandwidth.value) + 1:
                # Only perform this calculation if the TA's bandwidth is indeed
                # a decimal point. I.e. 10.48, and not 10.0.
                if int(ta.bandwidth.value) < ta.bandwidth.value:
                    bw_write = ta.bandwidth.value + cumulative_bw
                    val_write = ta.value + cumulative_val
            else:
                val_write = ta.compute_value_at_bandwidth(Kbps(bw)) +\
                            cumulative_val
                bw_write = bw + cumulative_bw

            visualization_points[ta.id_].append([bw_write, val_write])
            rows.append([str(bw_write), (val_write)])

        cumulative_bw += ta.bandwidth.value
        cumulative_val += ta.value


    with open(csv_output, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)

    return visualization_points

def export_raw(
        csv_output,
        optimizer,
        discretizer,
        opt_res,
        upper_bound_value,
        lower_bound_value,
        unadapted_value,
        channel_efficiency,
        seed):
    """Exports the raw results computed after one instance of the challenge problem is run

    :param str csv_output: The full path of the file to output to
    :param Optimizer optimizer: The optimizer used to solve this instance
    :param Discretizer discretizer: The discretizer used to solve this instance
    :param OptimizerResult opt_res: The optimization result
    :param int upper_bound_value: The upper bound value
    :param int lower_bound_value: The lower bound value
    :param int unadapted_value: The unadapted value of the solution after a perturbation
    :param {int: int} channel_efficiency: The output of running the bandwidth efficiency calculation
    :param int seed: The constraints object used in this instance
    """
    disc_count = ''
    accuracy = ''

    if isinstance(discretizer, AccuracyDiscretizer):
        accuracy = discretizer.accuracy
    disc_count = discretizer.disc_count

    channel_efficiency_print = channel_efficiency_print_value(channel_efficiency)

    with open(csv_output, 'a') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                seed,
                disc_count,
                accuracy,
                opt_res.value,
                upper_bound_value,
                lower_bound_value,
                unadapted_value,
                opt_res.run_time,
                opt_res.solve_time,
                channel_efficiency_print,
                len(opt_res.scheduled_tas)])


def update_mdl_schedule(schedules):
    """Updates the OrientDB database MDL file with the new schedule

    :param [<Schedule>] schedules: The schedule to use when updating the database
    """
    scenario_orientdb = OrientDBSession(
        database_name=MDL_DB,
        config_file=ORIENTDB_CONFIG_FILE)
    scenario_orientdb.open_database()
    scenario_orientdb.update_schedule(schedules)
    scenario_orientdb.close_database()


def import_shell_mdl_file():
    """Imports an MDL file. Written so that the start.py call to this function
    can happen in one line.
    """
    importer = OrientDBImporter(MDL_DB, MDL_SHELL_FILE,
                                ORIENTDB_CONFIG_FILE)
    importer.import_xml()
    importer.orientDB_helper.close_database()


def export_mdl(mdl_output):
    """Exports an MDL file to the specified file

    :param str mdl_output: The full path of the file to export the MDL database to
    """
    exporter = OrientDBExporter(
        MDL_DB,
        mdl_output,
        ORIENTDB_CONFIG_FILE)
    exporter.export_xml()
    exporter.orientDB_helper.close_database()


def mac_to_id(mac_address):
    """
    Translates a RadioLink ID to TA and Ground ID strings.

    i.e. RadioLink_4097to61473
                   /        \
           Src Radio RF    Dst Group RF
           MAC Address     MAC Address

    If you convert these numbers into their hex representations, you would get the following:
    4097  : 0x1001  : Ground Radio 1
    61473 : 0xF021  : Uplink for TA 2
    4129  : 0x1021  : TA 2 Radio
    61472 : 0xF020  : Downlink from TA 2

    •	All Source RF MAC Addresses start with first hex digit as 0x1
    •	All Destination RF MAC Addresses start with first hex digit as 0xF
    •	Second hex digit is 0x0 for all RF MAC Addresses
    •	Third hex digit represents location or test mission association: (0 = ground radio, 1 = TA 1, 2 = TA 2, 3 = TA3, etc.)
    •	Fourth hex digit represents radio number

    o	On ground radios, they increment: 00, 01, 02, etc.
    o	On a TA, we assume there is only one radio, so this digit is a 1.
    o	For RF Group MAC Addresses, ‘0’ is the downlink (transmitted by the TA, received by the ground) and ‘1’ is the uplink (transmitted by the ground, received by the TA).


    :param str mac_address: The ID field of a RadioLink element, i.e. RadioLink_4097to61473
    :returns (str, str) ids: The source TA id and Destination id. (source, destination)
    """
    ids = [int(s) for s in mac_address[10:].split('to') if s.isdigit()]
    source_mac = ids[0]
    destination_mac = ids[1]

    source_hex = hex(source_mac)
    destination_hex = hex(destination_mac)

    source_type = _determine_type(source_hex)
    destination_type = _determine_type(destination_hex)

    source_id = str((int(source_hex[4:6])))
    destination_id = str((int(destination_hex[4:6])))

    source = source_type + source_id
    destination = destination_type + destination_id

    return (source, destination)


def id_to_mac(ta_id, direction):
    """
    Takes in a TA ID and direction and translates it to a MAC Address according
    to the SwRI naming convention.
    i.e. TA100, up ---> RadioLink_4196to61540
         TA100, down ---> RadioLink_8292to61796

    :param str ta_id: The id to translate into a MAC Address
    :param str direction: The direction the transmission is going. i.e. TA to Ground (down) or Ground to TA (up).
    :returns str radio_link_mac: Returns a string representing the RadioLink formatted according to
    """
    id_number = int(re.sub("[^0-9]", "", ta_id))

    if direction == 'up':
        mac = str(GROUND_MAC + id_number) + '_to_' + str(UPLINK_MAC + id_number)
    else:
        mac = str(TA_MAC + id_number) + '_to_' + str(DOWNLINK_MAC + id_number)

    return 'RadioLink_' + mac


def _determine_type(x):
    """Takes as input a RadioLink ID string, parses the first 4 characters to determine
    the type of RadioLink this is. Can be one of four types; Uplink, Downlink,
    Ground or TA.
    These values are SwRI provided, and follow the convention they've set.

    :param str x: The RadioLink ID to determine the type of
    :returns str type: The type of RadioLink this is
    """
    y = x[0:4]

    if y == '0xf0':
        type = 'Uplink '
    elif y == '0xf1':
        type = 'Downlink '
    elif y == '0x10':
        type = 'Ground '
    elif y == '0x20':
        type = 'TA '
    else:
        raise MACAddressParseError(
            '{0} does not match any of the known abbreviations'.format(y),
            'MDLUtils._determine_type')

    return type
