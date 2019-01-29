"""

txop.py

Data object representing a TxOp node.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import TxOpInitializationError
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout


class TxOp:
    def __init__(
            self,
            start_usec,
            stop_usec,
            center_frequency_hz,
            txop_timeout,
            _rid=None):
        if not isinstance(start_usec, Microseconds):
            raise TxOpInitializationError(
                'start_usec must be of type microseconds {0}'.format(start_usec))
        if not isinstance(stop_usec, Microseconds):
            raise TxOpInitializationError(
                'stop_usec be of type microseconds: {0}'.format(stop_usec))
        if not isinstance(center_frequency_hz, Frequency):
            raise TxOpInitializationError(
                'center_frequency_hz: [{0}] must be an instance of type Frequency:'.format(center_frequency_hz))
        if not isinstance(txop_timeout, TxOpTimeout):
            raise TxOpInitializationError(
                'txop_timeout: [{0}] must be an instance of type TxOpTimeout:'.format(txop_timeout))
        if start_usec.value > stop_usec.value:
            raise TxOpInitializationError(
                'start_usec: [{0}] must be less than stop_usec: [{1}]'.format(
                    start_usec, stop_usec))

        self.start_usec = start_usec
        self.stop_usec = stop_usec
        self.center_frequency_hz = center_frequency_hz
        self.txop_timeout = txop_timeout
        self._rid = _rid
