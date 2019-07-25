import os
from cp1.common.logger import Logger
logger = Logger()
logger.setup_file_handler(os.path.abspath('../logs/'))
logger = logger.logger

from ortools.linear_solver import pywraplp
from copy import deepcopy
import time
import csv
import json
import sys
import re

from brass_mdl_tools.mdl_generator import generate_mdl_file
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.utils.data_generators.ta_generator import TAGenerator
from cp1.utils.data_generators.channel_generator import ChannelGenerator
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.utils.orientdb.orientdb_session import OrientDBSession
from cp1.utils.file_utils.mdl_utils import *
from cp1.processing.algorithms.scheduling.os_schedule import OSSchedule
from cp1.processing.algorithms.scheduling.greedy_schedule import GreedySchedule
from cp1.processing.algorithms.optimization.greedy_optimization import GreedyOptimization
from cp1.processing.algorithms.optimization.dynamic_program import DynamicProgram
from cp1.processing.algorithms.optimization.integer_program import IntegerProgram
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization


config_file = '../conf/data.json'
with open(config_file, 'r') as f:
    data = json.load(f)

    num_tas = data['TAs']['num_tas']
    num_channels = data['Channels']['num_channels']

    guard_band = Milliseconds(data['Constraints Object']['guard_band'])
    epoch = Milliseconds(data['Constraints Object']['epoch'])
    txop_timeout = TxOpTimeout(data['Constraints Object']['txop_timeout'])
    goal_throughput_bulk = BandwidthRate(BandwidthTypes.BULK, Kbps(
        data['Constraints Object']['goal_throughput_bulk']))
    goal_throughput_voice = BandwidthRate(BandwidthTypes.VOICE, Kbps(
        data['Constraints Object']['goal_throughput_voice']))
    goal_throughput_safety = BandwidthRate(BandwidthTypes.SAFETY, Kbps(
        data['Constraints Object']['goal_throughput_safety']))

    accuracy_disc_epsilons = data['Algorithms']['Discretization']['Accuracy']['epsilon']
    bandwidth_disc = data['Algorithms']['Discretization']['Bandwidth']['num_discretizations']
    value_disc = data['Algorithms']['Discretization']['Value']['num_discretizations']

    cbc = data['Algorithms']['Optimization']['CBC']
    gurobi = data['Algorithms']['Optimization']['Gurobi']
    greedy_algorithm = data['Algorithms']['Optimization']['Greedy']
    dynamic = data['Algorithms']['Optimization']['Dynamic Program']

    greedy_schedule = data['Algorithms']['Scheduling']['Greedy Schedule']
    os_schedule = data['Algorithms']['Scheduling']['OS Schedule']

    constraints_db_name = data['Files and Database']['constraints_db_name']
    mdl_db_name = data['Files and Database']['mdl_db_name']
    orientdb_config_file = os.path.abspath(
        data['Files and Database']['orientdb_config_file'])
    mdl_input_file = os.path.abspath(
        data['Files and Database']['mdl_input_file'])
    mdl_output_folder = os.path.abspath(
        data['Files and Database']['mdl_output_folder'])
    raw_output_folder = os.path.abspath(
        data['Files and Database']['raw_output_folder'])

generate_mdl_file(
    ta_count=3,
    output=mdl_input_file,
    base='../external/TxOpScheduleViewer/brass_mdl_tools/base.xml')
importer = OrientDBImporter(mdl_db_name, mdl_input_file,
                            orientdb_config_file)
importer.import_xml()
importer.orientDB_helper.close_database()

# Setup data
channel = Channel()
ta1 = TA(id_='TA1', minimum_voice_bandwidth=Kbps(500), minimum_safety_bandwidth=Kbps(3000), latency=Milliseconds(20), scaling_factor=1, c=0.005, bandwidth=Kbps(1500), channel=channel)
ta2 = TA(id_='TA2', minimum_voice_bandwidth=Kbps(500), minimum_safety_bandwidth=Kbps(1000), latency=Milliseconds(50), scaling_factor=1, c=0.005, bandwidth=Kbps(1000), channel=channel)
ta3 = TA(id_='TA3', minimum_voice_bandwidth=Kbps(500), minimum_safety_bandwidth=Kbps(1000), latency=Milliseconds(50), scaling_factor=1, c=0.005, bandwidth=Kbps(1000), channel=channel)
candidate_tas = [ta1, ta2, ta3]

constraints_object = ConstraintsObject(id_='C1', candidate_tas=candidate_tas, channels=[channel])
algorithm_result = AlgorithmResult(scheduled_tas=candidate_tas, run_time=0.5, solve_time=0.5, value=1000, constraints_object=constraints_object)


# Solve
greedy_schedule = GreedySchedule()
new_greedy_schedule = greedy_schedule.schedule(algorithm_result=algorithm_result)
new_greedy_schedule.sort(key=lambda x: x.start_usec.value, reverse=False)
for txop in new_greedy_schedule:
    print(mac_to_id(txop.radio_link_id), txop.start_usec.value, txop.stop_usec.value)

# os_schedule = OSSchedule()
# new_os_schedule = os_schedule.schedule(algorithm_result=algorithm_result)
# new_os_schedule.sort(key=lambda x: x.start_usec.value, reverse=False)
# for txop in new_os_schedule:
#     print(mac_to_id(txop.radio_link_id), txop.start_usec.value, txop.stop_usec.value)

# Update MDL File Schedule
scenario_orientdb = OrientDBSession(
    database_name=mdl_db_name,
    config_file=orientdb_config_file)
scenario_orientdb.open_database()
scenario_orientdb.update_schedule(new_greedy_schedule)
scenario_orientdb.close_database()

# Esport MDL File
exporter = OrientDBExporter(
    mdl_db_name,
    mdl_output_folder + '\\' + 'output_file' + '.xml',
    orientdb_config_file)
exporter.export_xml()
exporter.orientDB_helper.close_database()

#
# print("\nGreedy Schedule\n")
# greedy_schedule = GreedySchedule()
# new_greedy_schedule = greedy_schedule.schedule(algorithm_result=algorithm_result)
# new_greedy_schedule.sort(key=lambda x: x.start_usec.value, reverse=False)
# for txop in new_greedy_schedule:
#     print(mac_to_id(txop.radio_link_id), txop.start_usec.value, txop.stop_usec.value)
#
# print("\nOS Schedule\n")
# os_schedule = OSSchedule()
# new_os_schedule = os_schedule.schedule(algorithm_result=algorithm_result)
# new_os_schedule.sort(key=lambda x: x.start_usec.value, reverse=False)
# for txop in new_os_schedule:
#     print(mac_to_id(txop.radio_link_id), txop.start_usec.value, txop.stop_usec.value)
