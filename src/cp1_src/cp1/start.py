import os
from cp1.common.logger import Logger
logger = Logger()
logger.setup_file_handler(os.path.abspath('/data'))
logger = logger.logger

from ortools.linear_solver import pywraplp
from copy import deepcopy
from datetime import timedelta
import time
import csv
import json
import sys
import re
import shutil
import subprocess

from brass_mdl_tools.mdl_generator import generate_mdl_shell
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.utils.data_generators.ta_generator import TAGenerator
from cp1.utils.data_generators.channel_generator import ChannelGenerator
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.utils.orientdb.orientdb_session import OrientDBSession
from cp1.processing.algorithms.scheduling.greedy_schedule import GreedySchedule
from cp1.processing.algorithms.scheduling.hybrid_schedule import HybridSchedule
# from cp1.processing.algorithms.optimization.greedy_optimization import GreedyOptimization
from cp1.processing.algorithms.optimization.dynamic_program import DynamicProgram
from cp1.processing.algorithms.optimization.integer_program import IntegerProgram
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization


def import_mdl_file():
    importer = OrientDBImporter(mdl_db_name, mdl_shell_file,
                                orientdb_config_file)
    importer.import_xml()
    importer.orientDB_helper.close_database()

def export_mdl_file():
    exporter = OrientDBExporter(
        mdl_db_name,
        mdl_output,
        orientdb_config_file)
    exporter.export_xml()
    exporter.orientDB_helper.close_database()

def update_mdl_schedule(new_schedule):
    scenario_orientdb = OrientDBSession(
        database_name=mdl_db_name,
        config_file=orientdb_config_file)
    scenario_orientdb.open_database()
    scenario_orientdb.update_schedule(new_schedule.txop_list)
    scenario_orientdb.close_database()

def generate_constraints_objects():
    for seed in range(seeds[0], seeds[1] + 1):
        channels = ChannelGenerator(config_file).generate(seed)
        candidate_tas = TAGenerator(config_file).generate(channels, seed)

        for ta in candidate_tas:
            ta.eligible_channels = channels

        local_constraints_objects.append(ConstraintsObject(
            id_=1,
            candidate_tas=candidate_tas,
            channels=channels,
            seed=seed,
            goal_throughput_bulk=goal_throughput_bulk,
            goal_throughput_voice=goal_throughput_voice,
            goal_throughput_safety=goal_throughput_safety,
            guard_band=guard_band,
            epoch=epoch,
            txop_timeout=txop_timeout))

def store_and_retrieve_constraints():
    constraints_orientdb = OrientDBSession(
        database_name=constraints_db_name,
        config_file=orientdb_config_file)
    constraints_orientdb.open_database(over_write=True)
    for constraints_object in local_constraints_objects:
        constraints_orientdb.store_constraints(constraints_object)
    orientdb_constraints_objects = constraints_orientdb.get_constraints()
    constraints_orientdb.close_database()
    return orientdb_constraints_objects

def setup_scheduling_algorithms():
    if greedy_schedule == 1:
        scheduling_algorithms.append(GreedySchedule())
    if hybrid_schedule == 1:
        scheduling_algorithms.append(HybridSchedule())

def setup_discretization_algorithms():
    if accuracy_disc_epsilons:
        for x in accuracy_disc_epsilons:
            discretization_algorithms.append(AccuracyDiscretization(x))
    if bandwidth_disc:
        for x in bandwidth_disc:
            discretization_algorithms.append(BandwidthDiscretization(x))
    if value_disc:
        for x in value_disc:
            discretization_algorithms.append(ValueDiscretization(x))

def setup_optimization_algorithms(constraints_objects):
    if cbc == 1:
        for x in constraints_objects:
            optimization_algorithms.append(IntegerProgram(deepcopy(x)))
    if gurobi == 1:
        for x in constraints_objects:
            optimization_algorithms.append(Gurobi(deepcopy(x)))
    if dynamic == 1:
        for x in constraints_objects:
            optimization_algorithms.append(DynamicProgram(deepcopy(x)))
    # if greedy_algorithm == 1:
    #     for x in constraints_objects:
    #         optimization_algorithms.append(GreedyOptimization(deepcopy(x)))

def determine_file_name():
    if isinstance(discretization_algorithm, AccuracyDiscretization):
        disc_write_value = discretization_algorithm.accuracy
    else:
        disc_write_value = discretization_algorithm.num_discretizations
    return '{0}_{1}({2})_{3}_{4}_{5}'.format(schedule.channel_frequency, str(discretization_algorithm), disc_write_value, str(optimization_algorithm), str(scheduling_algorithm), timestamp)

def clear_files():
    folders = [raw_output_folder, mdl_output_folder]
    for folder in folders:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

def write_raw_results():
    if isinstance(discretization_algorithm, AccuracyDiscretization):
        num_discretizations = ''
        accuracy = discretization_algorithm.accuracy
    else:
        num_discretizations = discretization_algorithm.num_discretizations
        accuracy = ''

    ta_print_res = ''
    for ta in res.scheduled_tas:
        ta_print_res += (',{0}_{1}_{2}_{3}'.format(ta.id_,
                                                   ta.value,
                                                   ta.bandwidth.value,
                                                   ta.channel.frequency.value))

    bw_eff_print = ''
    for channel_frequency, efficiency in bw_eff.items():
        bw_eff_print += ('{0},{1}').format(channel_frequency, efficiency)
    bw_eff_print = bw_eff_print[:-1]

    with open(raw_output_folder + '\\' + file_name + '.csv', 'a') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='\\')
        csv_writer.writerow(
            [
                optimization_algorithm.constraints_object.seed,
                num_discretizations,
                accuracy,
                res.value,
                res_upper_bound.value,
                bw_eff_print,
                res.run_time,
                res.solve_time,
                ta_print_res])

logger.debug(
    '***************************Challenge Problem 1 Started*********************')
config_file = '../../../conf/data.json'
with open(config_file, 'r') as f:
    data = json.load(f)

    num_tas = data['TAs']['num_tas']
    num_channels = data['Channels']['num_channels']

    guard_band = timedelta(microseconds=1000*int(data['Constraints Object']['guard_band']))
    epoch = timedelta(microseconds=1000*int(data['Constraints Object']['epoch']))
    txop_timeout = TxOpTimeout(data['Constraints Object']['txop_timeout'])
    goal_throughput_bulk = BandwidthRate(BandwidthTypes.BULK, Kbps(
        data['Constraints Object']['goal_throughput_bulk']))
    goal_throughput_voice = BandwidthRate(BandwidthTypes.VOICE, Kbps(
        data['Constraints Object']['goal_throughput_voice']))
    goal_throughput_safety = BandwidthRate(BandwidthTypes.SAFETY, Kbps(
        data['Constraints Object']['goal_throughput_safety']))
    seeds = data['Constraints Object']['seeds']

    accuracy_disc_epsilons = data['Algorithms']['Discretization']['Accuracy']['epsilon']
    bandwidth_disc = data['Algorithms']['Discretization']['Bandwidth']['num_discretizations']
    value_disc = data['Algorithms']['Discretization']['Value']['num_discretizations']

    cbc = data['Algorithms']['Optimization']['CBC']
    gurobi = data['Algorithms']['Optimization']['Gurobi']
    greedy_algorithm = data['Algorithms']['Optimization']['Greedy']
    dynamic = data['Algorithms']['Optimization']['Dynamic']

    greedy_schedule = data['Algorithms']['Scheduling']['Greedy']
    hybrid_schedule = data['Algorithms']['Scheduling']['Hybrid']

    orientdb = data['Files and Database']['orientdb']
    visualize = data['Files and Database']['visualize']
    clear = data['Files and Database']['clear']
    constraints_db_name = data['Files and Database']['constraints_db_name']
    mdl_db_name = data['Files and Database']['mdl_db_name']
    mdl_shell_file = data['Files and Database']['mdl_shell_file']
    orientdb_config_file = os.path.abspath(
        data['Files and Database']['orientdb_config_file'])
    mdl_output_folder = os.path.abspath(
        data['Files and Database']['mdl_output_folder'])
    raw_output_folder = os.path.abspath(
        data['Files and Database']['raw_output_folder'])

if clear == 1:
    logger.info('Deleting previous runs...')
    clear_files()

scenario_orientdb = OrientDBSession(
    database_name=mdl_db_name,
    config_file=orientdb_config_file)
constraints_orientdb = OrientDBSession(
    database_name=mdl_db_name,
    config_file=orientdb_config_file)
local_constraints_objects = []
orientdb_constraints_objects = []
constraints_objects = []
discretization_algorithms = []
optimization_algorithms = []
scheduling_algorithms = []
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
mdl_output = ''

if orientdb == 1:
    logger.info('Generating MDL File...')
    generate_mdl_shell(
        ta_count=num_tas,
        output=mdl_shell_file,
        base='../../../external/TxOpScheduleViewer/brass_mdl_tools/base.xml')

    logger.info('Importing MDL File...')
    import_mdl_file()

logger.debug('Generating Constraints Objects...')
generate_constraints_objects()

logger.info('Storing and Retrieving Constraints in OrientDB...')
if orientdb == 1:
    constraints_objects = store_and_retrieve_constraints()
else:
    constraints_objects = local_constraints_objects

logger.info('Setting up Discretization Algorithms...')
setup_discretization_algorithms()

logger.debug('Setting up Optimization Algorithms...')
setup_optimization_algorithms(constraints_objects)

logger.debug('Setting up Scheduling Algorithms...')
setup_scheduling_algorithms()

for discretization_algorithm in discretization_algorithms:
    for optimization_algorithm in optimization_algorithms:
        logger.debug('Optimizing...')
        res = optimization_algorithm.optimize(discretization_algorithm, optimization_algorithm.constraints_object)
        res_upper_bound = optimization_algorithm.optimize_upper_bound(discretization_algorithm, optimization_algorithm.constraints_object)
        for ta in res.scheduled_tas:
            print(ta.id_, ta.latency.microseconds)
        # print('Algorithm Result: {0}'.format(res))
        # print('Upper Bound Algorithm Result: {0}'.format(res_upper_bound))

        for scheduling_algorithm in scheduling_algorithms:
            logger.info('Constructing schedule...')
            new_schedules = scheduling_algorithm.schedule(deepcopy(res))
            bw_eff = scheduling_algorithm.bw_efficiency_upper_bound(deepcopy(res))

            if orientdb == 1:
                logger.info('Generating new MDL Files...')
                for schedule in new_schedules:
                    update_mdl_schedule(schedule)

                    logger.debug('Writing results...')
                    file_name = determine_file_name()
                    mdl_output = mdl_output_folder + '\\' + file_name + '.xml'
                    write_raw_results()
                    export_mdl_file()
                    if visualize == 1:
                        os.system("start /wait cmd /c \
                                   python \
                                   c:/dev/cp1/external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py \
                                   {0}".format(mdl_output))
            logger.info('**********Optimization Algorithm: {0}, Discretization: {1}, Scheduling Algorithm: {2}*********'.format(optimization_algorithm, discretization_algorithm, scheduling_algorithm))
logger.debug(
    '***************************Challenge Problem 1 Complete********************')
