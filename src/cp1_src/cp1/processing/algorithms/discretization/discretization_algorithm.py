"""discretization_algorihtm.py

Interface for all discretization strategies.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc


class DiscretizationAlgorithm(abc.ABC):

    @abc.abstractmethod
    def discretize(self, tas, channels):
        pass
