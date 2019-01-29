"""

constraints_object.py

Data object representing a constraints object.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import ConstraintsObjectInitializationError
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.constraints.ta import TA
from cp1.data_objects.constraints.channel import Channel


class ConstraintsObject:
    def __init__(self, guard_band, epoch, candidate_tas, channel):
        """
        Constructor

        :param guard_band: The unused part of the radio spectrum between radio bands to prevent interference.
        :type guard_band: Microseconds

        :param epoch: Total allowable transmission time.
        :type epoch: Milliseconds

        :param candidate_tas: List of potential TA's.
        :type candidate_tas: List[TA]

        :param channel: Channel specific data such as the amount of throughput available
        :type channel: Channel
        """
        if not isinstance(guard_band, Microseconds):
            raise ConstraintsObjectInitializationError('guard_band must be an instance of Microseconds: {0}'.format(
                guard_band
            ), 'ConstraintsObject.__init__')
        if not isinstance(epoch, Milliseconds):
            raise ConstraintsObjectInitializationError('epoch must be an instance of Milliseconds: {0}'.format(
                epoch
            ), 'ConstraintsObject.__init__')

        if not all(isinstance(x, TA) for x in candidate_tas):
            raise ConstraintsObjectInitializationError('candidate_tas must only contain instances of TA: {0}'.format(
                candidate_tas
            ), 'ConstraintsObject.__init__')
        if not isinstance(channel, Channel):
            raise ConstraintsObjectInitializationError('channel be an instance of Channel: {0}'.format(
                channel
            ), 'ConstraintsObject.__init__')

        self.guard_band = guard_band
        self.epoch = epoch
        self.candidate_tas = candidate_tas
        self.channel = channel
