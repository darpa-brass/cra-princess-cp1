import re
import os
import sys
import json
import csv
from time import strftime

from ortools.linear_solver import pywraplp

from cp1.common.logger import Logger

from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.integer_program import IntegerProgram
from cp1.processing.algorithms.dynamic_program import DynamicProgram
from cp1.processing.algorithms.greedy import Greedy
from cp1.processing.algorithms.gurobi import Gurobi

from cp1.utils.orientdb_session import OrientDBSession
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.utils.channel_generator import ChannelGenerator
from cp1.utils.ta_generator import TAGenerator

from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel

logger = Logger().logger

# config_file = input("Enter path to your data.json file [cp1/conf/data.json]: ")
#
# if config_file == '':
#     config_file = '../../../conf/data.json'

config_file = '../../../conf/data.json'
logger.info('***************************Challenge Problem 1 Started*********************')
with open(config_file, 'r') as config_file:
    data = json.load(config_file)

    guard_band = Milliseconds(data['Constraints Object']['guard_band'])
    epoch = Milliseconds(data['Constraints Object']['epoch'])
    txop_timeout = TxOpTimeout(data['Constraints Object']['txop_timeout'])
    goal_throughput_bulk = BandwidthRate(BandwidthTypes.BULK, Kbps(
        data['Constraints Object']['goal_throughput_bulk']))
    goal_throughput_voice = BandwidthRate(BandwidthTypes.VOICE, Kbps(
        data['Constraints Object']['goal_throughput_voice']))
    goal_throughput_safety = BandwidthRate(BandwidthTypes.SAFETY, Kbps(
        data['Constraints Object']['goal_throughput_safety']))

    accuracy_disc_epsilons = data['Discretization Strategy']['Accuracy']['epsilon']
    bandwidth_disc_lower = data['Discretization Strategy']['Bandwidth']['num_discretizations'][0]
    bandwidth_disc_upper = data['Discretization Strategy']['Bandwidth']['num_discretizations'][1]
    value_disc_lower = data['Discretization Strategy']['Value']['num_discretizations'][0]
    value_disc_upper = data['Discretization Strategy']['Value']['num_discretizations'][1]

    cbc = data['Algorithm']['CBC']
    gurobi = data['Algorithm']['Gurobi']
    greedy = data['Algorithm']['Greedy Algorithm']
    dynamic = data['Algorithm']['Dynamic Program']

    constraints_db_name = data['Files and Database']['constraints_db_name']
    mdl_db_name = data['Files and Database']['mdl_db_name']
    mdl_output_file = data['Files and Database']['mdl_output_file']
    mdl_input_file = data['Files and Database']['mdl_input_file']
    remote_db_config_file = data['Files and Database']['remote_db_config_file']
    local_db_config_file = data['Files and Database']['local_db_config_file']
    raw_output_folder = data['Files and Database']['raw_output_folder']
    use_orientdb = data['Files and Database']['use_orientdb']


scenario_orientdb = OrientDBSession(
    database_name=mdl_db_name,
    config_file=local_db_config_file)
constraints_orientdb = OrientDBSession(
    database_name=constraints_db_name,
    config_file=local_db_config_file)

logger.info('***************************Generating TAs and Channels...***********************')
constraints_objects = []

channels = ChannelGenerator().generate()
candidate_tas = TAGenerator().generate()

for ta in candidate_tas:
    ta.eligible_channels = channels

constraints_objects.append(ConstraintsObject(
                                id_ = 1,
                                candidate_tas=candidate_tas,
                                channels=channels,
                                ta_seed='timestamp',
                                channel_seed='timestamp',
                                goal_throughput_bulk=goal_throughput_bulk,
                                goal_throughput_voice=goal_throughput_voice,
                                goal_throughput_safety=goal_throughput_safety,
                                guard_band=guard_band,
                                epoch=epoch,
                                txop_timeout=txop_timeout))

if use_orientdb == 1:
    logger.info(
        '***************************Clearing database...***********************')
    constraints_orientdb.open_database()

    logger.info(
        '***************************Storing Constraints Object...***********************')
    for constraints_object in constraints_objects:
        constraints_orientdb.create_constraints_object(constraints_object)

    logger.info(
        '***************************Retrieving Constraints...***********************')
    constraints_objects = [constraints_orientdb.get_constraints()]
    constraints_orientdb.close_database()

logger.debug(constraints_objects)

logger.info(
    '***************************Optimizing Schedule...**************************')
discretizations = []
if accuracy_disc_epsilons != 0:
    for x in accuracy_disc_epsilons:
        discretizations.append(AccuracyDiscretization(1-x))

if bandwidth_disc_lower != bandwidth_disc_upper:
    for x in range(bandwidth_disc_lower, bandwidth_disc_upper + 1):
        discretizations.append(BandwidthDiscretization(x))

if value_disc_lower != value_disc_upper:
    for x in range(value_disc_lower, value_disc_upper + 1):
        discretizations.append(ValueDiscretization(x))

########## Algorithms ##########
algorithms = []
if cbc == 1:
    for x in constraints_objects:
        algorithms.append(IntegerProgram(x))

if gurobi == 1:
    for x in constraints_objects:
        algorithms.append(Gurobi(x))

if dynamic == 1:
    for x in constraints_objects:
        algorithms.append(DynamicProgram(x))

if greedy == 1:
    for x in constraints_objects:
        algorithms.append(Greedy(x))

########## Run ##########
timestamp = strftime("%Y-%m-%d %H-%M-%S")
for discretization in discretizations:
    for algorithm in algorithms:

        # Optimize
        if isinstance(algorithm, Greedy):
            res = algorithm.optimize()
        else:
            res = algorithm.optimize(discretization)

        file_name = raw_output_folder + '/' + str(algorithm) + '_' + str(
            discretization) + '_' + timestamp + '.csv'

        discretization_write_value = None
        if isinstance(discretization, AccuracyDiscretization):
            num_discretizations = ''
            accuracy = discretization.accuracy
        else:
            num_discretizations = discretization.num_discretizations
            accuracy = ''

        ta_print_res = ''
        for ta in res.scheduled_tas:
            ta_print_res += (',{0}_{1}_{2}_{3}'.format(ta.id_, ta.value, ta.bandwidth.value, ta.channel.frequency.value))

        with open(file_name, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([algorithm.constraints_object.ta_seed, num_discretizations,
                                accuracy, res.value, res.run_time, res.solve_time, ta_print_res])
logger.info('***************************Challenge Problem Complete***********************')
