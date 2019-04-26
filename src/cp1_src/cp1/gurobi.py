"""integer_program.py

Algorithm that uses an integer program to selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
import math
import sys
from pandas import *
from gurobipy import *
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

class Gurobi:
    def __init__(self, discretization_strategy, constraints_object):
        self.discretization_strategy = discretization_strategy
        self.constraints_object = constraints_object
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
        start_time = time.perf_counter()
        tas = self.discretization_strategy.discretize(self.constraints_object)
        channels = []
        for channel in self.constraints_object.channels:
            channels.append([channel.frequency.value, channel.length.value, channel.latency.value, channel.capacity.value, self.constraints_object.guard_band.value])

        # m.setObjective(x + y + 2 * z, GRB.MAXIMIZE)
        m = Model('CP1')
        selected_tas = [[]] * (len(tas))
        for i in range(0, len(tas)):
            coeffs = []
            constrs = []
            for j in range(0, len(self.constraints_object.channels)):
                column_name = 'c_{0}'.format(j)
                if j == ((i // self.discretization_strategy.num_discretizations) % len(self.constraints_object.channels)):
                    coeffs.append(((tas[i][2]/channels[j][3])*channels[j][2]) + (2 * self.constraints_object.guard_band.value))
                    constrs.append(column_name)
                else:
                    coeffs.append(0)
                    constrs.append(column_name)
            for j in range(len(self.constraints_object.channels), len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
                column_name = 'c_{0}'.format(j)
                if i // (self.discretization_strategy.num_discretizations * len(self.constraints_object.channels)) == (j - len(self.constraints_object.channels)):
                    coeffs.append(1)
                    constrs.append(column_name)
                else:
                    coeffs.append(0)
                    constrs.append(column_name)
            col = Column(coeffs, constrs)
            selected_tas[i] = m.addVar(
                0, 1, tas[i][1], GRB.BINARY, '{0}_{1}_{2}'.format(tas[i][0], tas[i][3], tas[i][2]), column=col)

        solve_start = time.perf_counter()
        m.optimize()
        solve_time = time.perf_counter() - solve_start
        run_time = time.perf_counter() - start_time

        for v in m.getVars():
            print('%s %g' % (v.varName, v.x))
        print('Obj: %g' % m.objVal)

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
latency = Milliseconds(10)
guard_band = Milliseconds(1)
capacity = Kbps(1000)
epoch = Milliseconds(100)
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
integer = Gurobi(discretization_strategy, constraints_object)
