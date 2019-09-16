"""gurobi.py

Integer program written in Gurobi's Python API to select TAs for scheduling.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import time
import math
import sys
import csv
from pandas import *
from gurobipy import *
from cp1.data_objects.constants.constants import *
from cp1.data_objects.processing.optimizer_result import OptimizerResult
from cp1.algorithms.optimizers.optimizer import Optimizer
from cp1.common.logger import Logger

logger = Logger().logger


class Gurobi(Optimizer):
    def _optimize(self, constraints_object, discretized_tas, num_discretizations):
        # Setup data
        start_time = time.perf_counter()
        logger.debug('Beginning Gurobi Integer Program...')
        min_latency = self.retrieve_min_latency(discretized_tas)

        # Construct empty constraints
        m = Model()
        if INTEGER_PROGRAM_TIME_LIMIT is not None:
            m.Params.time_limit = INTEGER_PROGRAM_TIME_LIMIT

        ta_vector = [[]] * (len(discretized_tas))
        for i in range(0, len(constraints_object.channels) + len(constraints_object.candidate_tas)):
            m.addConstr(lhs=0, rhs=GRB.INFINITY,
                        sense=GRB.LESS_EQUAL, name='r_{0}'.format(i))
            m.update()

        for i in range(0, len(constraints_object.channels)):
            m.addConstr(lhs=-GRB.INFINITY, rhs=1, sense=GRB.LESS_EQUAL, name='r_{0}'.format(
                i + len(constraints_object.channels) + len(constraints_object.candidate_tas)))
            m.update()

        for i in range(0, len(ta_vector)):
            coeffs = []
            constrs = []

            # Constraint: TA must fit on specific channel
            for j in range(0, len(constraints_object.channels)):
                coeff = 0
                if j == ((i // num_discretizations) % len(constraints_object.channels)):
                    coeff = discretized_tas[i].compute_communication_length(constraints_object.channels[j].capacity, min_latency, constraints_object.guard_band)
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            # Constraint: Same TA must not communicate on multiple channels
            for j in range(len(constraints_object.channels), len(constraints_object.channels) + len(constraints_object.candidate_tas)):
                coeff = 0
                if i // (num_discretizations * len(constraints_object.channels)) == (j - len(constraints_object.channels)):
                    coeff = 1
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            # Constraint: TA only allowed to communicate over eligible_channels
            for j in range(len(constraints_object.channels) + len(constraints_object.candidate_tas), 2 * len(constraints_object.channels) + len(constraints_object.candidate_tas)):
                coeff = 1
                if discretized_tas[i].channel_is_eligible(constraints_object.channels[(i // num_discretizations) % len(constraints_object.channels)]):
                    coeff = 0
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            col = Column(coeffs, constrs)
            ta_vector[i] = m.addVar(
                lb=0, ub=1, obj=discretized_tas[i].value, vtype=GRB.BINARY, name='{0}_{1}_{2}'.format(discretized_tas[i].id_, discretized_tas[i].channel.frequency.value, discretized_tas[i].bandwidth.value), column=col)

        # Set the right hand side of all constraints
        for i in range(0, len(constraints_object.channels)):
            m.getConstrByName('r_{0}'.format(i)).setAttr('rhs', min_latency.get_microseconds())
        for i in range(len(constraints_object.channels), len(constraints_object.channels) + len(constraints_object.candidate_tas)):
            m.getConstrByName('r_{0}'.format(i)).setAttr('rhs', 1)
        for i in range(len(constraints_object.channels) + len(constraints_object.candidate_tas), 2 * len(constraints_object.channels) + len(constraints_object.candidate_tas)):
            m.getConstrByName('r_{0}'.format(i)).setAttr('rhs', 0)

        # Setup the objective function
        obj = LinExpr()
        for i in range(0, len(discretized_tas)):
            obj += discretized_tas[i].value * ta_vector[i]
        m.setObjective(obj, GRB.MAXIMIZE)

        # Solve
        solve_start = time.perf_counter()
        m.optimize()
        solve_time = time.perf_counter() - solve_start
        run_time = time.perf_counter() - start_time

        # Retrieve solution
        self.scheduled_tas = []
        vars = m.getVars()
        for i in range(0, len(vars)):
            if vars[i].x == 1:
                self.scheduled_tas.append(discretized_tas[i])
        value = sum(ta.value for ta in self.scheduled_tas)

        logger.debug('Gurobi completed in {0} seconds'.format(run_time))
        return OptimizerResult(constraints_object=constraints_object, scheduled_tas=self.scheduled_tas, solve_time=solve_time, run_time=run_time, value=value)

    def __str__(self):
        return 'Gurobi'

    __repr__ = __str__
