"""integer_program.py

Algorithm that uses an integer program to selects TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
import math
from pandas import *
from copy import deepcopy
from cp1.utils.decorators.timedelta import timedelta
from ortools.linear_solver import pywraplp
from cp1.common.logger import Logger
from cp1.data_objects.constants.constants import INTEGER_PROGRAM_ENGINE, INTEGER_PROGRAM_TIME_LIMIT
from cp1.algorithms.optimizers.optimizer import Optimizer
from cp1.data_objects.processing.optimizer_result import OptimizerResult

logger = Logger().logger


class IntegerProgram(Optimizer):
    def _optimize(self, constraints_object, discretized_tas, num_discretizations):
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
        :returns OptimizerResult:
        """
        logger.debug('Beginning CBC Integer Program...')
        start_time = time.perf_counter()

        min_latency = self.retrieve_min_latency(discretized_tas)

        solver = pywraplp.Solver('MDLScheduling', INTEGER_PROGRAM_ENGINE)
        solver.SetTimeLimit(INTEGER_PROGRAM_TIME_LIMIT * 1000)

        # Construct objective function
        ta_vector = [[]] * (len(discretized_tas))
        objective = solver.Objective()
        for i in range(0, len(discretized_tas)):
            variable_id = '{0}_{1}_{2}_{3}'.format(discretized_tas[i].id_, discretized_tas[i].channel.frequency.value, discretized_tas[i].bandwidth.value, i % num_discretizations)
            ta_vector[i] = solver.Var(
                0, 1, True, variable_id)
            objective.SetCoefficient(ta_vector[i], discretized_tas[i].value)

        # This is an IP maximization problem, whereby we are trying to find the subset of TAs that provide the maximum value, not minimum
        objective.SetMaximization()

        constraints = [] * len(constraints_object.channels)

        # Constraint: TAs must be able to fit on a given channel
        for i in range(0, len(constraints_object.channels)):
            constraints.append(solver.Constraint(-solver.infinity(), min_latency.microseconds))
            for j in range(0, len(discretized_tas)):
                coeff = 0
                if (math.floor(j / (num_discretizations)) % len(constraints_object.channels)) == i:
                        coeff = discretized_tas[j].compute_communication_length(constraints_object.channels[i].capacity, min_latency, constraints_object.guard_band).microseconds
                constraints[i].SetCoefficient(ta_vector[j], coeff)

        # Constraint: TAs cannot communicate on multiple channels simultaneously
        for i in range(0, len(constraints_object.candidate_tas)):
            constraints.append(solver.Constraint(-solver.infinity(), 1))
            for j in range(0, int(len(discretized_tas))):
                coeff = 0
                if math.floor(int(j) / int(len(constraints_object.channels) * (num_discretizations))) == i:
                    coeff = 1
                constraints[i + len(constraints_object.channels)].SetCoefficient(ta_vector[j], coeff)

        # Constraint: TAs only allowed to communicate on eligible channels
        constraints.append(solver.Constraint(-solver.infinity(), 0))
        for j in range(len(discretized_tas)):
            coeff = 1
            index_of_discretized_ta_channel = (int(j/num_discretizations)) % len(constraints_object.channels)
            if discretized_tas[j].channel_is_eligible(constraints_object.channels[index_of_discretized_ta_channel]):
                coeff = 0
            constraints[len(constraints_object.channels) + len(constraints_object.candidate_tas)].SetCoefficient(ta_vector[j], coeff)

        # Prints the model
        # print(solver.ExportModelAsLpFormat(False))

        # Solve and calculate run time
        solve_start = time.perf_counter()
        solver.Solve()
        solve_time = time.perf_counter() - solve_start

        # Retrieve solution
        scheduled_tas = []
        for i in range(0, len(discretized_tas)):
            ta_selected_by_or_tools = ta_vector[i].solution_value() > 0
            if ta_selected_by_or_tools:
                scheduled_tas.append(discretized_tas[i])

        value = self.compute_solution_value(scheduled_tas)

        run_time = time.perf_counter() - start_time
        logger.debug('CBC Integer Program complete in {0} seconds'.format(run_time))

        return OptimizerResult(scheduled_tas=scheduled_tas, solve_time=solve_time, run_time=run_time, value=value)

    def compute_upper_bound_optimization(self, constraints_object, discretized_tas):
        """Optimizes TAs without a latency requirement

        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :param [<TA>] discretized_tas: The list of discretized TA objects
        :returns OptimizerResult:
        """
        co = deepcopy(constraints_object)
        for ta in co.candidate_tas:
            ta.latency = co.epoch
        return self.optimize(co, discretized_tas)

    def __str__(self):
        return 'CBC'

    __repr__ = __str__
