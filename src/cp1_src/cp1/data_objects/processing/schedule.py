from cp1.data_objects.mdl.txop import TxOp
from cp1.common.exception_class import ScheduleInitializationException


class Schedule():
    def __init__(self, channel_frequency, txop_list):
        """Constructor
        :param int channel_frequency: The frequency this schedule is for
        :param [<TxOp>] txop_list: The list of TxOp nodes to enter into an MDL file
        """
        if not isinstance(channel_frequency, int):
            raise ScheduleInitializationException(
                'channel_frequency ({0}) must be an instance of int'.format(channel_frequency),
                'schedule.__init__()'
            )
        if not all(isinstance(txop, TxOp) for txop in txop_list):
            raise ScheduleInitializationException(
                'txop_list ({0}) must contain TxOp objects'.format(txop_list),
                'schedule.__init__()'
            )
        self.channel_frequency = channel_frequency
        self.txop_list = txop_list
