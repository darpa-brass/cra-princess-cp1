import re
import os
import sys

from ortools.linear_solver import pywraplp

from cp1.common.logger import Logger
from cp1.processing.algorithms.integer_program import IntegerProgram
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.optimization_algorithm import OptimizationAlgorithm
from cp1.processing.bandwidth_processor import BandwidthProcessor
from cp1.utils.orientdb_session import OrientDBSession
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.utils.constraint_types import ConstraintTypes

from brass_api.orientdb.brass_orientdb_client import BrassOrientDBClient
from brass_api.orientdb.orientdb_helper import BrassOrientDBHelper

logger = Logger().logger

logger.info(
    '***************************Challenge Problem 1 Started*********************')
scenario_database_name = 'cra_scenarios'
constraints_database_name = 'cra_constraints'
output_file = 'mdl_files/CRA_Scenarios_After_Adaptation.xml'
mdl_file = os.path.abspath('mdl_files/CRA_Scenarios_Before_Adaptation.xml')
remote_db_config_file = os.path.abspath('../../../conf/remote_db_config.json')
local_db_config_file = os.path.abspath('../../../conf/local_db_config.json')
bandwidth_file = os.path.abspath('../../../conf/mdl_ids.json')
config_file = os.path.abspath('../../../conf/config.json')
output_folder = os.path.abspath('../../../output/raw')

scenario_orientdb = OrientDBSession(
    database_name=scenario_database_name,
    config_file=remote_db_config_file)
constraints_orientdb = OrientDBSession(
    database_name=constraints_database_name,
    config_file=local_db_config_file)

########## Extract raw data ##########
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

    num_tas = data['TAs']['count']
    lower_ta_seed = data['TAs']['seeds'][0]
    upper_ta_seed = data['TAs']['seeds'][1]
    num_seeds = upper_ta_seed - lower_ta_seed
    lower_minimum_voice_bandwidth = Kbps(data['TAs']['voice_bandwidth'][0])
    upper_minimum_voice_bandwidth = Kbps(data['TAs']['voice_bandwidth'][1])
    lower_minimum_safety_bandwidth = Kbps(data['TAs']['safety_bandwidth'][0])
    upper_minimum_safety_bandwidth = Kbps(data['TAs']['safety_bandwidth'][1])
    lower_latency = Milliseconds(data['TAs']['latency'][0])
    upper_latency = Milliseconds(data['TAs']['latency'][1])
    lower_scaling_factor = data['TAs']['scaling_factor'][0]
    upper_scaling_factor = data['TAs']['scaling_factor'][1]
    lower_c = data['TAs']['c'][0]
    upper_c = data['TAs']['c'][1]

    num_channels = data['Channels']['count']
    channel_seed = data['Channels']['seed']
    lower_capacity = Kbps(data['Channels']['capacity'][0])
    upper_capacity = Kbps(data['Channels']['capacity'][1])

    accuracy_disc_epsilons = data['Discretization Strategy']['Accuracy']['epsilon']
    bandwidth_disc_lower = data['Discretization Strategy']['Bandwidth']['num_discretizations'][0]
    bandwidth_disc_upper = data['Discretization Strategy']['Bandwidth']['num_discretizations'][1]
    value_disc_lower = data['Discretization Strategy']['Value']['num_discretizations'][0]
    value_disc_upper = data['Discretization Strategy']['Value']['num_discretizations'][1]

    cbc = data['Algorithm']['CBC']
    gurobi = data['Algorithm']['Gurobi']
    greedy = data['Algorithm']['Greedy Algorithm']
    dynamic = data['Algorithm']['Dynamic Program']

logger.info(
    '***************************Generating TAs and Channels...***********************')
constraints_objects = []
channel_generator = ChannelGenerator(
                        lower_capacity=lower_capacity,
                        upper_capacity=upper_capacity,
                        seed=channel_seed)
channels = channel_generator.generate_uniformly(num_channels)
for seed in range(lower_ta_seed, upper_ta_seed + 1):
    ta_generator = TAGenerator(
                    lower_minimum_voice_bandwidth=lower_minimum_voice_bandwidth,
                    upper_minimum_voice_bandwidth=upper_minimum_voice_bandwidth,
                    lower_minimum_safety_bandwidth=lower_minimum_safety_bandwidth,
                    upper_minimum_safety_bandwidth=upper_minimum_safety_bandwidth,
                    lower_latency=lower_latency,
                    upper_latency=upper_latency,
                    lower_scaling_factor=lower_scaling_factor,
                    upper_scaling_factor=upper_scaling_factor,
                    lower_c=lower_c,
                    upper_c=upper_c,
                    seed=seed)
    candidate_tas = ta_generator.generate_uniformly(num_tas)
    for ta in candidate_tas:
        ta.eligible_channels = channels

    constraints_objects.append(ConstraintsObject(
                                    candidate_tas=candidate_tas,
                                    channels=channels,
                                    ta_seed=seed,
                                    channel_seed=channel_seed,
                                    goal_throughput_bulk=goal_throughput_bulk,
                                    goal_throughput_voice=goal_throughput_voice,
                                    goal_throughput_safety=goal_throughput_safety,
                                    guard_band=guard_band,
                                    epoch=epoch,
                                    txop_timeout=txop_timeout))

logger.info(
    '***************************Clearing database...***********************')
constraints_oriendb.delete_nodes_by_class('TA')
constraints_orientdb.delete_nodes_by_class('Channel')
constraints_orientdb.delete_nodes_by_class('Constraints Object')



logger.info(
    '***************************Storing channels and TAs...***********************')

logger.info(
    '***************************Retrieving Constraints...***********************')
constraints_object = constraints_orientdb.get_constraints()
logger.debug(constraints_object)

logger.info(
    '***************************Optimizing Schedule...**************************')
discretization_strategy = ValueDiscretization(accuracy=0.9)
solver_type = pywraplp.Solver.CPLEX_MIXED_INTEGER_PROGRAMMING
algorithm = IntegerProgram(discretization_strategy, solver_type)

schedule_processor = ScheduleProcessor(constraints_object)
schedule_processor.process(algorithm)

logger.info(
    '***************************Processing Bandwidth...*************************')
process_bandwidth = BandwidthProcessor(
    constraints_object, bandwidth_file, up_ratio=0.5)
bandwidth_rates = process_bandwidth.process()
logger.info(bandwidth_rates)

logger.info(
    '***************************Importing MDL file...***************************')
logger.info('Importing {0} into {1}'.format(mdl_file, scenario_database_name))
logger.info('Parsing MDL file into intermediary data object...')
importer = OrientDBImporter(scenario_database_name,
                            mdl_file, remote_db_config_file)
importer.import_xml()
importer.orientDB_helper.close_database()

logger.info(
    '***************************Updating MDL File Bandwidth...******************')
scenario_orientdb.open_database()
scenario_orientdb.update_bandwidth(bandwidth_rates)

logger.info(
    '***************************Updating MDL File Schedule...*******************')
scenario_orientdb.update_schedule(new_schedule)
scenario_orientdb.close_database()

logger.info(
    '***************************Exporting MDL File...***************************')
logger.info('Exporting {0} to {1}'.format(scenario_database_name, output_file))
exporter = OrientDBExporter(scenario_database_name,
                            output_file, remote_db_config_file)
exporter.export_xml()
exporter.orientDB_helper.close_database()

logger.info(
    '********************************Results************************************')
new_tas = set()
new_value = 0
for channel, ta_list in algorithm.selected_tas.items():
    new_value += channel.value
    for ta in ta_list:
        new_tas.add(ta.id_.value)

logger.info('New Schedule Value: {0}'.format(new_value))
logger.info('New Schedule TAs: {0}'.format(new_tas))
logger.info(
    '***************************Challenge Problem 1 Complete********************')
logger.info(
    '***************************************************************************\n')
