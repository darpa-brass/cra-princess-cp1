"""constraints_object.py

Data object representing a constraints object.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel


class ConstraintsObject:
    def __init__(self, goal_throughput_bulk, goal_throughput_voice,
                 goal_throughput_safety, latency, guard_band, epoch, txop_timeout, candidate_tas, channels):
        """
        Constructor

        :param BandwidthRate goal_throughput_bulk: The new value for all Bulk ServiceLevelProfiles.
        :param BandwidthRate goal_throughput_voice: The new value for all Voice ServiceLevelProfiles.
        :param BandwidthRate goal_throughput_safety: The new value for all Safety ServiceLevelProfiles.
        :param Milliseconds latency: The gap in time between transmissions for a given TA
        :param Milliseconds guard_band: The unused part of the radio spectrum between radio bands to prevent interference.
        :param TxOpTimeout txop_timeout: The timeout value for TxOp nodes
        :param List[TA] candidate_tas: List of potential TA's.
        :param List[Channel] channels: Channel specific data such as the amount of throughput available
        """
        self.goal_throughput_bulk = goal_throughput_bulk
        self.goal_throughput_voice = goal_throughput_voice
        self.goal_throughput_safety = goal_throughput_safety
        self.latency = latency
        self.guard_band = guard_band
        self.epoch = epoch
        self.txop_timeout = txop_timeout
        self.candidate_tas = candidate_tas
        self.channels = channels

    def __str__(self):
        return 'Goal Throughput Bulk: {0}, ' \
               'Goal Throughput Voice: {1}, ' \
               'Goal Throughput Safety: {2}, ' \
               'Latency: {3}, ' \
               'Guard Band: {4}, ' \
               'Epoch: {5}, ' \
               'TxOp Timeout: {6}, ' \
               'Candidate TAs: [{7}], ' \
               'Channels: [{8}]'.format(
               self.goal_throughput_bulk,
               self.goal_throughput_voice,
               self.goal_throughput_safety,
               self.latency,
               self.guard_band.value,
               self.epoch.value,
               self.txop_timeout,
               self.candidate_tas,
               self.channels
               )

    def __eq__(self, other):
        if isinstance(other, ConstraintsObject):
            tas_equal = True
            for i in range(0, len(self.candidate_tas)):
                if self.candidate_tas[i] != other.candidate_tas[i]:
                    tas_equal = False

            channels_equal = True
            for i in range(0, len(self.channels)):
                if self.channels[i] != other.channels[i]:
                    channels_equal = False

            return (self.goal_throughput_bulk == other.goal_throughput_bulk and
                    self.goal_throughput_voice == other.goal_throughput_voice and
                    self.goal_throughput_safety == other.goal_throughput_safety and
                    self.latency == other.latency and
                    self.guard_band == other.guard_band and
                    self.epoch == other.epoch and
                    self.txop_timeout == other.txop_timeout and
                    tas_equal and
                    channels_equal)
        return False
