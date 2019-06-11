import re
import os
import sys
import json
import csv
from time import strftime
from ortools.linear_solver import pywraplp

from brass_mdl_tools.mdl_generator import generate_mdl_files

from cp1.common.logger import Logger
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.optimization.integer_program import IntegerProgram
from cp1.processing.algorithms.optimization.dynamic_program import DynamicProgram
from cp1.processing.algorithms.optimization.greedy_optimization import GreedyOptimization
# from cp1.processing.algorithms.optimization.gurobi import Gurobi
from cp1.processing.algorithms.scheduling.greedy_schedule import GreedySchedule
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


print('***************************Challenge Problem 1 Started*********************')
config_file = 'C:/dev/cp1/conf/data.json'
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
    greedy_algorithm = data['Algorithms']['Optimization']['Greedy Algorithm']
    dynamic = data['Algorithms']['Optimization']['Dynamic Program']

    greedy_schedule = data['Algorithms']['Scheduling']['Greedy Schedule']

    constraints_db_name = data['Files and Database']['constraints_db_name']
    mdl_db_name = data['Files and Database']['mdl_db_name']
    mdl_output_file = data['Files and Database']['mdl_output_file']
    mdl_input_file = data['Files and Database']['mdl_input_file']
    raw_output_folder = data['Files and Database']['raw_output_folder']

print('Generating Constraints Objects...')
channels = ChannelGenerator(config_file).generate()
candidate_tas = TAGenerator(config_file).generate()

constraints_objects = []
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

print('Setting up Discretization Algorithms...')
discretizations = []
if accuracy_disc_epsilons:
    for x in accuracy_disc_epsilons:
        discretizations.append(AccuracyDiscretization(1-x))
if bandwidth_disc:
    for x in bandwidth_disc:
        discretizations.append(BandwidthDiscretization(x))
if value_disc:
    for x in value_disc:
        discretizations.append(ValueDiscretization(x))

print('Setting up Optimization Algorithms...')
optimization_algorithms = []
if cbc == 1:
    for x in constraints_objects:
        optimization_algorithms.append(IntegerProgram(x))
if gurobi == 1:
    for x in constraints_objects:
        optimization_algorithms.append(Gurobi(x))
if dynamic == 1:
    for x in constraints_objects:
        optimization_algorithms.append(DynamicProgram(x))
if greedy_algorithm == 1:
    for x in constraints_objects:
        optimization_algorithms.append(GreedyOptimization(x))

print('Setting up Scheduling Algorithms...')
scheduling_algorithms = []
if greedy_schedule == 1:
    scheduling_algorithms.append(GreedySchedule())

timestamp = strftime("%Y-%m-%d %H-%M-%S")
for discretization in discretizations:
    for optimization_algorithm in optimization_algorithms:
        print('Optimizing...')
        res = optimization_algorithm.optimize(discretization)

        print('Writing raw results...')
        file_name = raw_output_folder + '/' + str(optimization_algorithm) + '_' + str(
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
            csv_writer.writerow([optimization_algorithm.constraints_object.ta_seed, num_discretizations,
                                accuracy, res.value, res.run_time, res.solve_time, ta_print_res])

        for scheduling_algorithm in scheduling_algorithms:
            print('Constructing schedule...')
            new_schedule = scheduling_algorithm.schedule(res, optimization_algorithm.constraints_object)
            print('New Schedule is:')
            print(new_schedule)
            #
            # print('Updating MDL File Schedule...')
            # scenario_orientdb.open_database()
            # scenario_orientdb.update_schedule(new_schedule)
            # scenario_orientdb.close_database()
            #
            # print('Exporting {0} to {1}'.format(mdl_output_file, mdl_output_file))
            # exporter = OrientDBExporter(mdl_db_name, mdl_output_file, local_db_config_file)
            # exporter.export_xml()
            # exporter.orientDB_helper.close_database()
            # sys.exit()

print('Challenge Problem 1 Complete.')
