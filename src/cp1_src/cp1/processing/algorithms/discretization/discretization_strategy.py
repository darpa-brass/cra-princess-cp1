"""discretization_strategy.py

Interface for all discretization strategies.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc


class DiscretizationStrategy(abc.ABC):
    @abc.abstractmethod
    def discretize(self, constraints_object):
        pass

    @abc.abstractmethod
    def discretize_one_channel(self, constraints_object):
        pass
