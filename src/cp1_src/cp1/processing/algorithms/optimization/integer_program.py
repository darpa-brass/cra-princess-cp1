"""integer_program.py

Algorithm that uses an integer program to selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
import math
from pandas import *
from ortools.linear_solver import pywraplp
#from cp1.common.logger import Logger
from cp1.processing.algorithms.optimization.optimization_algorithm import OptimizationAlgorithm
from cp1.processing.algorithms.optimization.ortools_solvers import ORToolsSolvers
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.processing.algorithm_result import AlgorithmResult

logger = Logger().logger


class IntegerProgram(OptimizationAlgorithm):
    def __init__(self, constraints_object, solver_type=ORToolsSolvers.CBC.value):
        self.constraints_object = constraints_object
        self.solver_type = solver_type

    def optimize(self, discretization_algorithm, time_limit=15):
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
        print('Beginning CBC Integer Program...')
        start_time = time.perf_counter()

        # Setup data
        discretized_tas = discretization_algorithm.discretize(self.constraints_object.candidate_tas, self.constraints_object.channels)

        min_latency = float(min(discretized_tas, key=lambda ta: ta.latency.value).latency.value)
        solver = pywraplp.Solver('MDLScheduling', self.solver_type)
        if time_limit is not None:
            solver.SetTimeLimit(time_limit * 1000)

        # Construct objective function
        ta_vector = [[]] * (len(discretized_tas))
        objective = solver.Objective()
        for i in range(0, len(discretized_tas)):
            ta_vector[i] = solver.Var(
                0, 1, True, '{0}_{1}_{2}_{3}'.format(discretized_tas[i].id_, discretized_tas[i].channel.frequency.value, discretized_tas[i].bandwidth.value, i % discretization_algorithm.num_discretizations))
            objective.SetCoefficient(ta_vector[i], discretized_tas[i].value)
        objective.SetMaximization()

        constraints = [] * len(self.constraints_object.channels)

        # Constraint: TA must fit on specific channel
        for i in range(0, len(self.constraints_object.channels)):
            constraints.append(solver.Constraint(-solver.infinity(), min_latency))
            for j in range(0, len(discretized_tas)):
                coeff = 0
                if (math.floor(j / (discretization_algorithm.num_discretizations)) % len(self.constraints_object.channels)) == i:
                        coeff = discretized_tas[j].compute_communication_length(self.constraints_object.channels[i].capacity, Milliseconds(min_latency), self.constraints_object.guard_band)
                constraints[i].SetCoefficient(ta_vector[j], coeff)

        # Constraint: Same TA must not communicate on multiple channels
        for i in range(0, len(self.constraints_object.candidate_tas)):
            constraints.append(solver.Constraint(-solver.infinity(), 1))
            for j in range(0, int(len(discretized_tas))):
                coeff = 0
                if math.floor(int(j) / int(len(self.constraints_object.channels) * (discretization_algorithm.num_discretizations))) == i:
                    coeff = 1
                constraints[i + len(self.constraints_object.channels)].SetCoefficient(ta_vector[j], coeff)

        # Constraint: TAs only allowed to communicate on specific channel
        for i in range(0, len(self.constraints_object.channels)):
            constraints.append(solver.Constraint(-solver.infinity(), 0))
            for j in range(0, len(discretized_tas)):
                coeff = 1
                if discretized_tas[j].channel_is_eligible(self.constraints_object.channels[i]):
                    coeff = 0
                constraints[i + len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)].SetCoefficient(ta_vector[j], coeff)

        # Prints the model
        # print(solver.ExportModelAsLpFormat(False))

        # Solve and calculate run time
        solve_start = time.perf_counter()
        solver.Solve()
        solve_time = time.perf_counter() - solve_start
        run_time = time.perf_counter() - start_time

        # Retrieve solution
        self.scheduled_tas = []
        for i in range(0, len(discretized_tas)):
            if ta_vector[i].solution_value() > 0:
                self.scheduled_tas.append(discretized_tas[i])
        value = sum(ta.value for ta in self.scheduled_tas)

        print('CBC Integer Program complete in {0} seconds'.format(run_time))
        return AlgorithmResult(scheduled_tas=self.scheduled_tas, solve_time=solve_time, run_time=run_time, value=value)

    def __str__(self):
        return 'CBC'

    __repr__ = __str__
