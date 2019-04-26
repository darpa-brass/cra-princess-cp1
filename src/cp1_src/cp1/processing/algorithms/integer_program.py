"""integer_program.py

Algorithm that uses an integer program to selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
from pandas import *
import math
# from cplex import *
# from cp1.processing.algorithms.discretization.discretization_strategy import DiscretizationStrategy
from cp1.processing.algorithms.optimization_algorithm import OptimizationAlgorithm
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from ortools.linear_solver import pywraplp
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.utils.ta_generator import TAGenerator
from cp1.utils.channel_generator import ChannelGenerator
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.constraints_object import ConstraintsObject



class IntegerProgram:
    def __init__(self, solver_type, discretization_strategy, constraints_object, time_limit=None):
        self.solver_type = solver_type
        self.discretization_strategy = discretization_strategy
        self.constraints_object = constraints_object
        self.time_limit = time_limit
        self.result = self.optimize()

    def optimize(self):
        """Uses Integer Programming to select TAs for scheduling.
        Uses the Google OR Tools `API <https://developers.google.com/optimization/mip/integer_opt>`.
        This wraps any of 4 C++ based Linear Programs in Python:
        1. `CBC <https://projects.coin-or.org/Cbc>` (Default)
        2. `SCIP <https://scip.zib.de/>`
        3. `GLPK <https://www.gnu.org/software/glpk/>`
        4. `Gurobi <http://www.gurobi.com/>`

        To use a different MILP Solver you can follow the directions `here <https://developers.google.com/optimization/install/python/source_windows>`.
        There is also a `Github <https://github.com/google/or-tools/issues/421>`ticket you can follow.

        :param ConstraintsObject constraints_object: A Constraints Object containing all data necessary to optimize over.
        :param SolverType solver_type: The type of Mixed Integer Program solver to use. Can be GLPK, CPLEX, GUROBI or CBC.
        """
        #start_time = time.perf_counter()
        start_time = time.time()
        tas = self.discretization_strategy.discretize(self.constraints_object)
        channels = []
        for channel in self.constraints_object.channels:
            channels.append([channel.frequency.value, channel.length.value, channel.latency.value,
                             channel.capacity.value, self.constraints_object.guard_band.value])

        solver = pywraplp.Solver('MDLScheduling', self.solver_type)
        if self.time_limit is not None:
            solver.SetTimeLimit(time_limit)

        selected_tas = [[]] * (len(tas))
        objective = solver.Objective()
        for i in range(0, len(tas)):
            #Tyler edited and added another parameter in variable name to avoid duplicates from accuracy discretization
            selected_tas[i] = solver.Var(
                0, 1, True, '{0}_{1}_{2}_{3}'.format(tas[i][0].id_, tas[i][3], tas[i][2], i%self.discretization_strategy.num_discretizations))
            objective.SetCoefficient(selected_tas[i], tas[i][1])
        objective.SetMaximization()

        constraints = [] * len(channels)
        for i in range(0, len(channels)):
            constraints.append(
                solver.Constraint(-solver.infinity(), channels[i][2]))
            for j in range(0, len(tas)):
                if (math.floor(j / (self.discretization_strategy.num_discretizations)) % len(channels)) == i:
                    constraints[i].SetCoefficient(selected_tas[j], ((
                        tas[j][2]/channels[i][3])*channels[i][2]) + (2 * self.constraints_object.guard_band.value))
                else:
                    constraints[i].SetCoefficient(selected_tas[j], 0)

        for i in range(0, len(self.constraints_object.candidate_tas)):
            constraints.append(solver.Constraint(-solver.infinity(), 1))
            for j in range(0, int(len(tas))):
                if math.floor(int(j) / int(len(channels) * (self.discretization_strategy.num_discretizations))) == i:
                    constraints[i + len(channels)
                                ].SetCoefficient(selected_tas[j], 1)
                else:
                    constraints[i + len(channels)
                                ].SetCoefficient(selected_tas[j], 0)

        solve_start = time.perf_counter()

        print(solver.Solve())

        solve_time = time.perf_counter() - solve_start
        #run_time = time.perf_counter() - start_time
        run_time = time.time() - start_time

        # Prints out the constraints
        # print(solver.ExportModelAsLpFormat(False))
        # # file = open("Integer 10ta 2ch.csv", "a")
        # # print('Integer Program:')

        file = open("Integer 100ta 3ch_accuracy.csv", "a")
        value = 0
        scheduled_tas = []
        for i in range(0, len(tas)):
            if selected_tas[i].solution_value() > 0:
                value += tas[i][1]
                scheduled_tas.append(tas[i][0])
                file.write('{0}, value: {1}, bandwidth: {2}, channel: {3}\n'.format(tas[i][0].id_, tas[i][1], tas[i][2], tas[i][3]))

        #file.write('{0}, {1}, {2}, {3}\n'.format(value, run_time, self.discretization_strategy.accuracy, self.discretization_strategy.num_discretizations))
        file.close()
        return AlgorithmResult(selected_tas=scheduled_tas, solve_time=solve_time, run_time=run_time, value=value)


# TAs
num_tas = 1
num_channels = 4
lower_minimum_voice_bandwidth=Kbps(50)
lower_minimum_safety_bandwidth=Kbps(100)
upper_minimum_voice_bandwidth=Kbps(200)
upper_minimum_safety_bandwidth=Kbps(100)
lower_scaling_factor=1
upper_scaling_factor=2
lower_c=0.001
upper_c=0.01

# Channels
br = BandwidthRate(BandwidthTypes.VOICE, Kbps(100))
lower_length = Milliseconds(100)
upper_length = Milliseconds(200)
lower_latency = Milliseconds(50)
upper_latency = Milliseconds(100)
fixed_latency = Milliseconds(50)
lower_capacity = Kbps(1000)
upper_capacity = Kbps(10000)
fixed_capacity = Kbps(10000)

# Constraints Object
epoch = Milliseconds(100)
txop_timeout = TxOpTimeout(255)
guard_band = Milliseconds(1)

# Algorithms
solver_type = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING

# Run algorithms
results = []
collection = [2]
print('Started')
for i in collection:
    print('i in coll')
    for j in range(1, 2):
        print('j in range')
        discretization_strategy = BandwidthDiscretization(2)
        lower_latency = Milliseconds(50)
        upper_latency = Milliseconds(50)
        ta_generator = TAGenerator(
                                lower_minimum_voice_bandwidth,
                                upper_minimum_voice_bandwidth,
                                lower_minimum_safety_bandwidth,
                                upper_minimum_safety_bandwidth,
                                lower_scaling_factor,
                                upper_scaling_factor,
                                lower_c,
                                upper_c)
        candidate_tas = ta_generator.generate(num_tas)
        print('generated TAs')

        channel_generator = ChannelGenerator(num_channels,
                                             lower_length,
                                             upper_length,
                                             lower_latency,
                                             upper_latency,
                                             lower_capacity,
                                             upper_capacity)
        channels = channel_generator.generate()
        print('generated_channels')
        constraints_object = ConstraintsObject(br, br, br, fixed_latency, guard_band, epoch, txop_timeout, candidate_tas, channels)

        cbc = IntegerProgram(pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING, discretization_strategy, constraints_object)
        print("Finished optimization")
