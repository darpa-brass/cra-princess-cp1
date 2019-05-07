"""discretization_strategy.py

Interface for all discretization strategies.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc


class DiscretizationStrategy(abc.ABC):

    @abc.abstractmethod
    def discretize(self, tas, channels):
        pass
