import sys
import csv
import json
from time import strftime
from ortools.linear_solver import pywraplp
from cp1.processing.algorithms.integer_program import IntegerProgram
from cp1.processing.algorithms.dynamic_program import DynamicProgram
from cp1.processing.algorithms.greedy import Greedy
from cp1.processing.algorithms.gurobi import Gurobi
from cp1.utils.ta_generator import TAGenerator
from cp1.utils.channel_generator import ChannelGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization


########## Extract raw data ##########
config_file = '../../../conf/config.json'
output_folder = '../../../output/raw'

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

########## Generate TAs and Channels ##########
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

########## Discretization Strategies ##########
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

        file_name = output_folder + '/' + str(algorithm) + '_' + str(
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
