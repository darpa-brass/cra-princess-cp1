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
from cp1.data_objects.mdl.kbps import Kbps
from cp1.utils.ta_generator import TAGenerator
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.processing.channel import Channel
from cp1.utils.channel_generator import ChannelGenerator
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.processing.algorithms.dynamic_program import DynamicProgram
from cp1.data_objects.processing.algorithm_result import AlgorithmResult
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.processing.algorithms.optimization_algorithm import OptimizationAlgorithm
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.common.logger import Logger

logger = Logger().logger


class Gurobi(OptimizationAlgorithm):
    def __init__(self, constraints_object):
        self.constraints_object = constraints_object

    def optimize(self, discretization_strategy, time_limit=15):
        # Setup data
        start_time = time.perf_counter()
        logger.debug('Beginning Gurobi Integer Program...')
        discretized_tas = discretization_strategy.discretize(self.constraints_object.candidate_tas, self.constraints_object.channels)
        min_latency = min(discretized_tas, key=lambda ta: ta.latency.value).latency.value

        # Construct empty constraints
        m = Model()
        if time_limit is not None:
            m.Params.time_limit = time_limit

        ta_vector = [[]] * (len(discretized_tas))
        for i in range(0, len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
            m.addConstr(lhs=0, rhs=GRB.INFINITY,
                        sense=GRB.LESS_EQUAL, name='r_{0}'.format(i))
            m.update()

        for i in range(0, len(self.constraints_object.channels)):
            m.addConstr(lhs=-GRB.INFINITY, rhs=1, sense=GRB.LESS_EQUAL, name='r_{0}'.format(
                i + len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)))
            m.update()

        for i in range(0, len(ta_vector)):
            coeffs = []
            constrs = []

            # Constraint: TA must fit on specific channel
            for j in range(0, len(self.constraints_object.channels)):
                coeff = 0
                if j == ((i // discretization_strategy.num_discretizations) % len(self.constraints_object.channels)):
                    coeff = discretized_tas[i].compute_communication_length(self.constraints_object.channels[j].capacity, Milliseconds(min_latency), self.constraints_object.guard_band)
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            # Constraint: Same TA must not communicate on multiple channels
            for j in range(len(self.constraints_object.channels), len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
                coeff = 0
                if i // (discretization_strategy.num_discretizations * len(self.constraints_object.channels)) == (j - len(self.constraints_object.channels)):
                    coeff = 1
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            # Constraint: TAs only allowed to communicate on specific channel
            for j in range(len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas), 2 * len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
                coeff = 1
                if discretized_tas[i].channel_is_eligible(self.constraints_object.channels[(i // discretization_strategy.num_discretizations) % len(self.constraints_object.channels)]):
                    coeff = 0
                coeffs.append(coeff)
                constrs.append(m.getConstrByName('r_{0}'.format(j)))

            col = Column(coeffs, constrs)
            ta_vector[i] = m.addVar(
                lb=0, ub=1, obj=discretized_tas[i].value, vtype=GRB.BINARY, name='{0}_{1}_{2}'.format(discretized_tas[i].id_, discretized_tas[i].channel.frequency.value, discretized_tas[i].bandwidth.value), column=col)

        # Set the right hand side of all constraints
        for i in range(0, len(self.constraints_object.channels)):
            m.getConstrByName('r_{0}'.format(i)).setAttr('rhs', min_latency)
        for i in range(len(self.constraints_object.channels), len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
            m.getConstrByName('r_{0}'.format(i)).setAttr('rhs', 1)
        for i in range(len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas), 2 * len(self.constraints_object.channels) + len(self.constraints_object.candidate_tas)):
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
        scheduled_tas = []
        vars = m.getVars()
        for i in range(0, len(vars)):
            if vars[i].x == 1:
                scheduled_tas.append(discretized_tas[i])
        value = sum(ta.value for ta in scheduled_tas)

        logger.debug('Gurobi completed in {0} seconds'.format(run_time))
        return AlgorithmResult(scheduled_tas=scheduled_tas, solve_time=solve_time, run_time=run_time, value=value)

    def __str__(self):
        return 'Gurobi'

    __repr__ = __str__
