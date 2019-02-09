"""

constraints_object.py

Data object representing a constraints object.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.constraints.ta import TA
from cp1.data_objects.constraints.channel import Channel
from cp1.common.exception_class import ConstraintsObjectInitializationException


class ConstraintsObject:
    def __init__(self, goal_throughput_bulk, goal_throughput_voice,
                    goal_throughput_safety, latency, guard_band, epoch, candidate_tas, channel):
        """
        Constructor

        :param goal_throughput_bulk: The new value for all Bulk ServiceLevelProfiles.
        :type goal_throughput_bulk: BandwidthRate

        :param goal_throughput_voice: The new value for all Voice ServiceLevelProfiles.
        :type goal_throughput_voice: BandwidthRate

        :param goal_throughput_safety: The new value for all Safety ServiceLevelProfiles.
        :type goal_throughput_safety: BandwidthRate

        :param latency: The gap in time between transmissions for a given TA
        :type latency: Milliseconds

        :param guard_band: The unused part of the radio spectrum between radio bands to prevent interference.
        :type guard_band: Milliseconds

        :param candidate_tas: List of potential TA's.
        :type candidate_tas: List[TA]

        :param channel: Channel specific data such as the amount of throughput available
        :type channel: Channel
        """
        if not isinstance(goal_throughput_bulk, BandwidthRate):
            raise ConstraintsObjectInitializationException('goal_throughput_bulk must be an instance of BandwidthRate:\nvalue: {0}\ntype: {1}'.format(
                goal_throughput_bulk, type(goal_throughput_bulk)
            ), 'ConstraintsObject.__init__')
        if not isinstance(goal_throughput_voice, BandwidthRate):
            raise ConstraintsObjectInitializationException('goal_throughput_voice must be an instance of BandwidthRate:\nvalue: {0}\ntype: {1}'.format(
                goal_throughput_voice, type(goal_throughput_voice)
            ), 'ConstraintsObject.__init__')
        if not isinstance(goal_throughput_safety, BandwidthRate):
            raise ConstraintsObjectInitializationException('goal_throughput_safety must be an instance of BandwidthRate:\nvalue: {0}\ntype: {1}'.format(
                goal_throughput_safety, type(goal_throughput_safety)
            ), 'ConstraintsObject.__init__')
        if not isinstance(latency, Milliseconds):
            raise ConstraintsObjectInitializationException('latency must be an instance of Milliseconds:\nvalue: {0}\ntype: {1}'.format(
                latency, type(latency)
            ), 'ConstraintsObject.__init__')
        if not isinstance(guard_band, Milliseconds):
            raise ConstraintsObjectInitializationException('guard_band must be an instance of Milliseconds:\nvalue: {0}\ntype: {1}'.format(
                guard_band, type(guard_band)
            ), 'ConstraintsObject.__init__')
        if not isinstance(epoch, Milliseconds):
            raise ChannelInitializationException('epoch must be an instance of Epoch:\nvalue: {0}\ntype: {1}'.format(
            epoch, type(epoch)
            ), 'Channel.__init__')
        if not all(isinstance(x, TA) for x in candidate_tas):
            raise ConstraintsObjectInitializationException('candidate_tas must only contain instances of TA:\nvalue: {0}\ntype: {1}'.format(
                candidate_tas, type(candidate_tas)
            ), 'ConstraintsObject.__init__')
        if not isinstance(channel, Channel):
            raise ConstraintsObjectInitializationException('channel be an instance of Channel:\nvalue: {0}\ntype: {1}'.format(
                channel, type(channel)
            ), 'ConstraintsObject.__init__')

        self.goal_throughput_bulk = goal_throughput_bulk
        self.goal_throughput_voice = goal_throughput_voice
        self.goal_throughput_safety = goal_throughput_safety
        self.latency = latency
        self.guard_band = guard_band
        self.epoch = epoch
        self.candidate_tas = candidate_tas
        self.channel = channel

    def __str__(self):
        ta_str = ''
        for ta in self.candidate_tas:
            ta_str += '<' + str(ta) + '>\n'
        return 'Goal Throughput Bulk: {0}, Goal Throughput Voice: {1}, Goal Throughput Safety: {2}, Latency: {3}, Guard Band: {4}, Epoch: {5}, Candidate TAs: [{6}], Channel: [{7}]'.format(self.goal_throughput_bulk, self.goal_throughput_voice, self.goal_throughput_safety, self.latency,
                                                                                    self.guard_band.value,
                                                                                    self.epoch.value,
                                                                                      ta_str,
                                                                                      self.channel)
