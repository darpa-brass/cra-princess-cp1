"""optimization_algorithm.py

Interface for algorithms.
"""
import abc
from ortools.linear_solver import pywraplp


class OptimizationAlgorithm(abc.ABC):
    @abc.abstractmethod
    def __init__(self, constraints_object):
        pass

    @abc.abstractmethod
    def optimize(self):
        pass
