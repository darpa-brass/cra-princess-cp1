"""
optimization_algorithm.py

Interface for algorithms.
"""
import abc
from ortools.linear_solver import pywraplp


class OptimizationAlgorithm(abc.ABC):
    @abc.abstractmethod
    def optimize(self, constraints_object):
        pass
