"""discretizer.py

Abstract base class for all discretization strategies.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc
from copy import deepcopy


class Discretizer(abc.ABC):
    @abc.abstractmethod
    def _discretize(self, constraints_object):
        """Selects TAs at specific bandwidth values according to the number of discretizations or accuracy

        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :returns [<TA>]:
        """
        pass

    def discretize(self, constraints_object):
        """Discretizes on a copy of the constraints_object

        :param ConstraintsObject constraints_object: The Constraints to use in an instance of a Challenge Problem.
        :returns [<TA>]:
        """
        co = deepcopy(constraints_object)
        discretized_co = self._discretize(co)
        return discretized_co
