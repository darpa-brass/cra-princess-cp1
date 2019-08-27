"""file_utils.py

Any helper functions related to parsing MDL files.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import re
import csv
import os

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
    database_name=MDL_DB,
    config_file=ORIENTDB_CONFIG_FILE)

    constraints_orientdb.open_database()
    orientdb_constraints_object_list = constraints_orientdb.store_and_retrieve_constraints(constraints_object_list)
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


def determine_file_name(discretizer, optimizer, scheduler, timestamp, perturb_tas=None):
    """Determines the appropriate name for an MDL or RAW output file

    :param Discretizer discretizer: The discretizer used to solve this instance
    :param Optimizer optimizer: The optimizer used to solve this instance
    :param Scheduler scheduler: The scheduler used to solve this instance
    :param str timestamp: The time this was executed
    :param [<TA>] perturb_tas: The list of TAs to perturb. If is not None, \'Perturbed\' is appended to file name.

    :returns str file_name: A name for the output file
    """
    if isinstance(discretizer, AccuracyDiscretizer):
        disc_write_value = discretizer.accuracy
    else:
        disc_write_value = discretizer.disc_count
    file_name = '{0}({1})_{2}_{3}_{4}'.format(str(discretizer), disc_write_value, str(optimizer), str(scheduler), timestamp)

    if perturb_tas is not None:
        file_name = 'Perturbed_' + file_name

    return file_name

def export_raw(csv_output, optimizer, discretizer, opt_res, upper_opt_res, bw_eff, co):
    """Exports the raw results computed after one instance of the challenge problem is run

    :param str csv_output: The full path of the file to output to
    :param Optimizer optimizer: The optimizer used to solve this instance
    :param Discretizer discretizer: The discretizer used to solve this instance
    :param OptimizerResult opt_res: The optimization result
    :param OptimizerResult upper_opt_res: The upper bound optimization result
    :param {int: int} bw_eff: The output of running the bandwidth efficiency calculation
    :param ConstraintsObject co: The constraints object used in this instance
    """
    disc_count = ''
    accuracy = ''
    if isinstance(discretizer, AccuracyDiscretizer):
        accuracy = discretizer.accuracy
    elif isinstance(discretizer, (BandwidthDiscretizer, ValueDiscretizer)):
        disc_count = discretizer.disc_count

    ta_print = ''
    for channel, tas in opt_res.scheduled_tas.items():
        for ta in tas:
            ta_print += ('{0}_{1}_{2}_{3},'.format(ta.id_,
                                                       ta.value,
                                                       ta.bandwidth.value,
                                                       channel.frequency.value))
    ta_print = ta_print[:-1]

    bw_eff_print = ''
    for channel_frequency, efficiency in bw_eff.items():
        bw_eff_print += ('{0}_{1},').format(channel_frequency, efficiency)
    bw_eff_print = bw_eff_print[:-1]

    with open(csv_output, 'a') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='\\')
        csv_writer.writerow(
            [
                co.seed,
                disc_count,
                accuracy,
                opt_res.value,
                upper_opt_res.value,
                opt_res.run_time,
                opt_res.solve_time,
                bw_eff_print,
                ta_print])


def update_mdl_schedule(schedules):
    """Updates the OrientDB database MDL file with the new schedule

    :param [<Schedule>] schedules: The schedule to use when updating the database
    """
    print(schedules)
    scenario_orientdb = OrientDBSession(
        database_name=MDL_DB,
        config_file=ORIENTDB_CONFIG_FILE)
    scenario_orientdb.open_database()
    scenario_orientdb.update_schedule(schedules)
    scenario_orientdb.close_database()


def import_shell_mdl_file():
    """Imports an MDL file
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
        mac = str(GROUND_MAC + id_number) + 'to' + str(UPLINK_MAC + id_number)
    else:
        mac = str(TA_MAC + id_number) + 'to' + str(DOWNLINK_MAC + id_number)

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
        raise MACAddressParseError('{0} does not match any of the known abbreviations'.format(y), 'MDLUtils._determine_type')

    return type
