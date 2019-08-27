"""constraints_object.py

Data object representing a constraints object.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.utils.decorators.timedelta import timedelta
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.constants.constants import MDL_MIN_INTERVAL
from cp1.utils.string_utils import *


class ConstraintsObject:
    def __init__(self,
                 id_,
                 candidate_tas,
                 channels,
                 seed,
                 goal_throughput_bulk=BandwidthRate(
                     BandwidthTypes.BULK, Kbps(100)),
                 goal_throughput_voice=BandwidthRate(
                     BandwidthTypes.VOICE, Kbps(100)),
                 goal_throughput_safety=BandwidthRate(
                     BandwidthTypes.SAFETY, Kbps(100)),
                 guard_band=timedelta(microseconds=1000),
                 epoch=timedelta(microseconds=100000),
                 txop_timeout=TxOpTimeout(255)
                ):
        """
        Constructor

        :param BandwidthRate goal_throughput_bulk: The new value for all Bulk ServiceLevelProfiles.
        :param BandwidthRate goal_throughput_voice: The new value for all Voice ServiceLevelProfiles.
        :param BandwidthRate goal_throughput_safety: The new value for all Safety ServiceLevelProfiles.
        :param timedelta guard_band: The unused part of the radio spectrum between radio bands to prevent interference.
        :param timedelta epoch: The epoch of the MDL file.
        :param TxOpTimeout txop_timeout: The timeout value for TxOp nodes
        :param List[TA] candidate_tas: List of potential TA's.
        :param List[Channel] channels: Channel specific data such as the amount of throughput available
        :param int seed: The number that was used to seed the random generator
        """
        self.goal_throughput_bulk = goal_throughput_bulk
        self.goal_throughput_voice = goal_throughput_voice
        self.goal_throughput_safety = goal_throughput_safety
        self.guard_band = guard_band
        self.epoch = epoch
        self.txop_timeout = txop_timeout
        self.candidate_tas = candidate_tas
        self.channels = channels
        self.seed = seed
        self.id_ = id_
        self.deadline_window = guard_band + MDL_MIN_INTERVAL


    def __str__(self):
        ta_str = ''
        for ta in self.candidate_tas:
            ta_str += str(ta) + '\n'

        channel_str = ''
        for channel in self.channels:
            channel_str += str(channel) + '\n'

        return 'ID: {0}\n\
Goal Throughput Bulk: {1}\n\
Goal Throughput Voice: {2}\n\
Goal Throughput Safety: {3}\n\
Guard Band: {4}\n\
Epoch: {5}\n\
TxOp Timeout: {6}\n\
Candidate TAs: {7}\
Channels: {8}'.format(
                   self.id_,
                   self.goal_throughput_bulk,
                   self.goal_throughput_voice,
                   self.goal_throughput_safety,
                   self.guard_band.microseconds,
                   self.epoch.microseconds,
                   self.txop_timeout,
                   ta_str,
                   channel_str
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
                    self.guard_band == other.guard_band and
                    self.epoch == other.epoch and
                    self.txop_timeout == other.txop_timeout and
                    self.id_ == other.id_,
                    tas_equal and
                    channels_equal)
        return False

    __repr__ = __str__
