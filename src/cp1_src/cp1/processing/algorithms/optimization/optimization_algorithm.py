"""optimization_algorithm.py

Interface for algorithms.
"""
import abc
from ortools.linear_solver import pywraplp
from datetime import timedelta
from cp1.data_objects.constants.constants import MDL_MIN_INTERVAL
from copy import deepcopy


class OptimizationAlgorithm(abc.ABC):
    @abc.abstractmethod
    def __init__(self, constraints_object):
        pass

    @abc.abstractmethod
    def optimize(self, constraints_object, discretization_algorithm):
        pass

    def optimize_upper_bound(self, constraints_object, discretization_algorithm):
        for ta in self.constraints_object.candidate_tas:
            ta.latency = self.constraints_object.epoch
        return self.optimize(deepcopy(constraints_object), discretization_algorithm)

    def round_bandwidth_values(self, scheduled_tas, channel = None):
        for ta in scheduled_tas:
            time_from_minimum_discretization = timedelta(microseconds=(((ta.bandwidth.value / ta.channel.capacity.value) * ta.latency.microseconds) %  MDL_MIN_INTERVAL.microseconds))
            if time_from_minimum_discretization > timedelta(microseconds=0):
                additional_bandwidth_required = ta.compute_bandwidth_requirement(ta.channel.capacity, ta.latency, time_from_minimum_discretization)
                ta.bandwidth += additional_bandwidth_required

    def round_bandwidth_value(self, ta, channel):
        time_from_minimum_discretization = timedelta(microseconds=(((ta.bandwidth.value / channel.capacity.value) * ta.latency.microseconds) %  MDL_MIN_INTERVAL.microseconds))
        if time_from_minimum_discretization > timedelta(microseconds=0):
            additional_bandwidth_required = ta.compute_bandwidth_requirement(channel.capacity, ta.latency, time_from_minimum_discretization)
            ta.bandwidth += additional_bandwidth_required
