"""optimizer.py

Abstract base class for all optimization algorithms.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc
from collections import defaultdict
from copy import deepcopy
from cp1.utils.decorators.timedelta import timedelta
from ortools.linear_solver import pywraplp
from cp1.data_objects.constants.constants import MDL_MIN_INTERVAL


class Optimizer(abc.ABC):
    @abc.abstractmethod
    def _optimize(self, constraints_object, discretized_tas, num_discretizations):
        """Selects TAs to communicate at certain bandwidth values on certain channels.

        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :param [<TA>] discretized_tas: The list of discretized TA objects
        :param int num_discretizations: The number of discretizations used. Useful for figuring out which discretized TA belongs to which Channel.
        :returns OptimizerResult:
        """
        pass

    def optimize(self, constraints_object, discretized_tas, num_discretizations):
        """Optimizes on a deepcopy of the constraints_object, and then rounds bandwidth values

        :param int num_discretizations: The number of discretizations a TA has
        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :param [<TA>] discretized_tas: The list of discretized TA objects
        :returns OptimizerResult:
        """
        return self._optimize(constraints_object, discretized_tas, num_discretizations)
        
    def retrieve_min_latency(self, ta_list):
        """Returns the min latency from a list of TAs

        :param [<TA>] ta_list: The list of TAs to select the min latency from
        :returns timedelta: A wrapped timedelta object representing min_latency in milliseconds
        """
        return min(ta_list, key=lambda x: x.latency).latency

    def compute_solution_value(self, scheduled_tas):
        """Returns the value of all TAs in the list of scheduled TAs
        :param [<TA>] scheduled_tas: The list of selected TAs
        :returns int: The solution value
        """
        return sum(ta.value for ta in scheduled_tas)
