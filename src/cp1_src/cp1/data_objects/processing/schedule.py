from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.common.exception_class import ScheduleInitializationException


class Schedule():
    def __init__(self, channel, txops):
        """Constructor
        :param Channel channel: The frequency this schedule is for
        :param [<TxOp>] txops: The list of TxOp nodes to be assigned to this channel in an MDL file
        """
        if not isinstance(channel, Channel):
            raise ScheduleInitializationException(
                'channel ({0}) must be an instance of int'.format(channel),
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


    def compute_and_set_schedule_value(self, constraints_object):
        """Computes the total value a TA provides at a certain bandwidth

        :param ConstraintsObject constraints_object: The constraints this schedule was created under
        """
        self.txops.sort(key=lambda x: x.start_usec, reverse=True)

        comm_time = 0
        for txop in self.txops:
            comm_time += txop.stop_usec - txop.start_usec

        comm_time_ms = ta_communication_time.microseconds / 1000
        bw = txop.ta.channel.capacity.value / ta_communication_time_ms
        val = txop.ta.compute_value(ta_bandwidth)


    def __str__(self):
        return '{0}: {1}'.format(self.channel, self.txops)

    __repr__ = __str__
