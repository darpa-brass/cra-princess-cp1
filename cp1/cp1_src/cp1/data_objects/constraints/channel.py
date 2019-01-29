"""

channel.py

Data object representing a radio channel.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.common.exception_class import ChannelInitializationError
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.mdl_id import MdlId


class Channel:
    def __init__(self, name, capacity, timeout, frequency):
        """
        Constructor

        :param name: Name of the channel.
        :type name: MdlId

        :param capacity: Total capacity of the channel in kbps.
        :type capacity: Kbps

        :param timeout: Timeout of channel in ms
        :type timeout: TxOpTimeout

        :param frequency: Channel's frequency
        :type frequency: Frequency
        """
        if not isinstance(name, MdlId):
            raise ChannelInitializationError('Name must be a str: {0}'.format(
                name
            ), 'Channel.__init__')
        if not isinstance(capacity, Kbps):
            raise ChannelInitializationError('Capacity must be an instance of Kbps: {0}'.format(
                capacity
            ), 'Channel.__init__')
        if not isinstance(timeout, TxOpTimeout):
            raise ChannelInitializationError('Timeout must be an instance of TxOpTimeout: {0}'.format(
                timeout
            ), 'Channel.__init__')
        if not isinstance(frequency, Frequency):
            raise ChannelInitializationError('Frequency must be an instance of Frequency: {0}'.format(
                frequency
            ), 'Channel.__init__')

        self.name = name
        self.capacity = capacity
        self.timeout = timeout
        self.frequency = frequency
