import sys
from cp1.gurobi import Gurobi
from cp1.processing.algorithms.integer_program import IntegerProgram
from cp1.processing.algorithms.dynamic_program import DynamicProgram
from cp1.utils.ta_generator import TAGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization



# TAs
num_tas = 10
lower_minimum_voice_bandwidth=Kbps(50)
lower_minimum_safety_bandwidth=Kbps(100)
upper_minimum_voice_bandwidth=Kbps(200)
upper_minimum_safety_bandwidth=Kbps(100)
lower_scaling_factor=1
upper_scaling_factor=5
lower_c=0.001
upper_c=0.01

# Channels
br = BandwidthRate(BandwidthTypes.VOICE, Kbps(100))
latency = Milliseconds(50)
guard_band = Milliseconds(1)
capacity = Kbps(1000)
epoch = Milliseconds(1000)
frequency = Frequency(4919500000)
txop_timeout = TxOpTimeout(255)

# Algorithms
num_discretizations = 10
scaling_factor = 2
discretization_strategy = BandwidthDiscretization(num_discretizations)

# Constraints Object
generator = TAGenerator(lower_minimum_voice_bandwidth,
                        upper_minimum_voice_bandwidth,
                        lower_minimum_safety_bandwidth,
                        upper_minimum_safety_bandwidth,
                        lower_scaling_factor,
                        upper_scaling_factor,
                        lower_c,
                        upper_c)
candidate_tas = generator.generate(num_tas)
channels = [Channel(frequency, epoch, latency, capacity)]
constraints_object = ConstraintsObject(br, br, br, latency, guard_band, epoch, txop_timeout, candidate_tas, channels)

# Run algorithms
integer = Gurobi(integer_program_engine, discretization_strategy, constraints_object)


# sys.setrecursionlimit(999999)
# , Channel(frequency4, epoch, latency, capacity), Channel(frequency3, epoch, latency, capacity), Channel(frequency2, epoch, latency, capacity)]
# frequency2 = Frequency(4919600000)
# frequency3 = Frequency(4919700000)
# frequency4 = Frequency(4919800000)
# Print Results
# Dynamic Program
# print('Dynamic Program:')
# dynamic_value=0
# for k, v in dynamic.sol.items():
#     for ta in v:
#         dynamic_value += ta[1]
#         print('bandwidth: {0}, {1}, value: {2}, bandwidth: {3}'.format(k, ta[0].id_, ta[1], ta[2]))
# print('Total Value: {0}'.format(dynamic_value))

# sys.setrecursionlimit(999999)
# dynamic_time_start = time.time()
# dynamic = DynamicProgram(discretization_strategy, constraints_object, scaling_factor)
# dynamic_time_end = time.time()

# # Print Results
# # Dynamic Program
# file = open("Dynamic 10ta 2ch.csv", "a")
# file.write('Dynamic Program: TAs: {0}, discretizations {1}, channels: {2}, Latency{3}\n'.format(num_tas, num_discretizations, len(channels), latency))
# dynamic_value=0
# for k, v in dynamic.sol.items():
#     for ta in v:
#         dynamic_value += ta[1]
#         file.write('bandwidth: {0}, {1}, value: {2}, bandwidth: {3}\n'.format(k, ta[0].id_, ta[1], ta[2]))
# file.write('Total Value: {0}\n'.format(dynamic_value))
# file.write("Dynamic programming time: {0}\n\n".format(dynamic_time_end - dynamic_time_start))
# file.close()



# #######################old run script end############################
# # Setup sol
# sol = {}
# for channel in constraints_object.channels:
#     sol[channel.frequency.value] = []
#
# remaining_tas = constraints_object.candidate_tas
# # Delete already schedule TAs
# for k, v in sol:
#     print(v)
#     # for x in range(0, len(remaining_tas)):
#     #     for ta in v:
#     #         if ta[0].id_ == remaining_tas[x].id_:
#     #             remaining_tas.pop(x)
#     #             break


# # Integer Program
# print(integer.result)

# print(DataFrame(alg.table))
# alg.retrieve_tas(num_tas, latency.value * 2)
# total_val = 0



# sum = 0
# for ta in candidate_tas:
#     print('TA: {0}, bandwidth: {1}'.format(ta.id_, ta.total_minimum_bandwidth.value))
#     sum += ta.total_minimum_bandwidth.value
#     print('Total Bandwidth: {0}'.format(sum))
