"""schedule.py

Class to hold schedules for each channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from collections import defaultdict
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.common.exception_class import ScheduleInitializationException
from cp1.utils.decorators.timedelta import timedelta


class Schedule():
    def __init__(self, channel, txops):
        """Constructor
        :param Channel channel: The frequency this schedule is for
        :param [<TxOp>] txops: The list of TxOp nodes to be assigned to this channel in an MDL file
        """
        if not isinstance(channel, Channel):
            raise ScheduleInitializationException(
                'channel ({0}) must be an instance of Channel'.format(channel),
                'schedule.__init__()'
            )
        if not all(isinstance(txop, TxOp) for txop in txops):
            raise ScheduleInitializationException(
                'txops ({0}) must contain TxOp objects'.format(txops),
                'schedule.__init__()'
            )
        self.channel = channel
        self.txops = txops


    def schedule_is_empty(self):
        """Utility function to determine if this schedule is empty

        :returns Boolean: True if empty
        """
        return len(self.txops) == 0

    def compute_value(self, constraints_object):
        """Computes the total value of the schedule

        :param ConstraintsObject constraints_object: The constraints this schedule was created under
        :returns int value: The total value of this schedule
        """
        value = 0

        values_by_ta = self.compute_value_ta(constraints_object)
        for ta, value in values_by_ta.items():
            value += value

        return value

    def compute_value_ta(self, constraints_object):
        """Computes the total value for each indidividual TA

        :param ConstraintsObject constraints_object: The constraints this schedule was created under
        :returns Dict[TA: int]: A dictionary of TA to it's value provided
        """
        values_by_ta = {}

        # Group TxOps by TA
        txops_by_ta = defaultdict(list)
        for txop in self.txops:
            txops_by_ta[txop.ta].append(txop)

        # Sort by start time
        for ta, txops in txops_by_ta.items():
            txops.sort(key=lambda x: x.start_usec, reverse=True)

        for ta, txops in txops_by_ta.items():
            comm_len = timedelta(microseconds=0)
            for txop in txops:
                comm_len += txop.stop_usec - txop.start_usec

            bw = ta.compute_bw_from_comm_len(ta.channel.capacity, ta.latency, comm_len)
            values_by_ta[ta] = ta.compute_value_at_bandwidth(bw)

        return values_by_ta

    def compute_bw_efficiency(self):
        """Computes the total bandwidth efficiency in this schedule."""
        comm_len = timedelta(microseconds=0)
        for txop in self.txops:
            comm_len += txop.stop_usec - txop.start_usec

        bw_eff =  comm_len / timedelta(microseconds=100000)
        return bw_eff

    def __str__(self):
        return '{0}: {1}'.format(self.channel, self.txops)

    __repr__ = __str__
