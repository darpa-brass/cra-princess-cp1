"""

ta.py

Data object representing a TA.

Author: Tameem Samawi (tsamawi@cra.com)

"""

from cp1.common.exception_class import TAInitializationError
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId


class TA:
    def __init__(
            self,
            id_,
            minimum_voice_bandwidth,
            minimum_safety_bandwidth,
            scaling_factor,
            c,
            utility_threshold):
        """
        Constructor

        :param id_: The ID of the TA.
        :type id_: str

        :param minimum_voice_bandwidth: The minimum required voice bandwidth to get this TA in the air.
        :type minimum_voice_bandwidth: str

        :param minimum_safety_bandwidth: The minimum required safety bandwidth to get this TA in the air.
        :type minimum_safety_bandwidth: int

        :param scaling_factor: The amount by which to scale the overall value by onc.
        :type scaling_factor: int

        :param c: The coefficient of a sample value function. For now it's set to 1 because there is no real value
                  function.
        :type c: int

        :param utility_threshold: A measure of how much value the given TA provides to the mission if the minimum amount
                                  of bandwidth is provided.
        :type utility_threshold: int
        """
        if not isinstance(id_, MdlId):
            raise TAInitializationError(
                'id must be str: {0}'.format(id), 'TA._init')
        if not isinstance(minimum_voice_bandwidth, Kbps):
            raise TAInitializationError(
                'minimum_voice_bandwidth must be instance of Kbps: {0}'.format(minimum_voice_bandwidth), 'TA._init')
        if not isinstance(minimum_safety_bandwidth, Kbps):
            raise TAInitializationError(
                'minimum_safety_bandwidth must be instance of Kbps: {0}'.format(minimum_safety_bandwidth), 'TA._init')
        if not (isinstance(scaling_factor, int) or isinstance(scaling_factor, float)):
            raise TAInitializationError(
                'scaling_factor must be int or float: {0}'.format(scaling_factor), 'TA._init')
        if not (isinstance(c, int) or isinstance(c, float)):
            raise TAInitializationError(
                'c must be int or float: {0}'.format(c), 'TA._init')
        if not isinstance(utility_threshold, int):
            raise TAInitializationError(
                'utility_threshold must be int: {0}'.format(utility_threshold), 'TA._init')

        self.id_ = id_
        self.minimum_voice_bandwidth = minimum_voice_bandwidth
        self.minimum_safety_bandwidth = minimum_safety_bandwidth
        self.scaling_factor = scaling_factor
        self.c = c
        self.utility_threshold = utility_threshold
        self.total_minimum_bandwidth = Kbps(minimum_voice_bandwidth.value + minimum_safety_bandwidth.value)
