"""

channel.py

Data object representing a radio channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import ChannelInitializationException
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.milliseconds import Milliseconds


class Channel:
    def __init__(self, name, capacity, timeout, frequency):
        """
        Constructor

        :param name: Name of the channel.
        :type name: MdlId

        :param timeout: Timeout of channel in ms
        :type timeout: TxOpTimeout

        :param frequency: Channel's frequency
        :type frequency: Frequency
        """
        if not isinstance(name, MdlId):
            raise ChannelInitializationException('Name must be an instance of MdlId:\nvalue: {0}\ntype: {1}'.format(
                name, type(name)
            ), 'Channel.__init__')
        if not isinstance(timeout, TxOpTimeout):
            raise ChannelInitializationException('Timeout must be an instance of TxOpTimeout:\nvalue: {0}\ntype: {1}'.format(
                timeout, type(timeout)
            ), 'Channel.__init__')
        if not isinstance(frequency, Frequency):
            raise ChannelInitializationException('Frequency must be an instance of Frequency:\nvalue: {0}\ntype: {1}'.format(
                frequency, type(frequency)
            ), 'Channel.__init__')

        self.name = name
        self.timeout = timeout
        self.frequency = frequency

    def __str__(self):
        return 'name: {0}, timeout: {1}, frequency: {2}'.format(self.name,
                                                   self.timeout.value,
                                                   self.frequency.value)
