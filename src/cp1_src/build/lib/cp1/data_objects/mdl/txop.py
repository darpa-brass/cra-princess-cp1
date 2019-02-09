"""

txop.py

Data object representing a TxOp node.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import TxOpInitializationException
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
            raise TxOpInitializationException(
                'start_usec must be of type microseconds.\nvalue: {0}, type: {1}'.format(start_usec, type(start_usec)))
        if not isinstance(stop_usec, Microseconds):
            raise TxOpInitializationException(
                'stop_usec be of type microseconds.\nvalue: {0}, type: {1}'.format(stop_usec, type(stop_usec)))
        if not isinstance(center_frequency_hz, Frequency):
            raise TxOpInitializationException(
                'center_frequency_hz must be an instance of type Frequency.\nvalue: {0}, type: {1}'.format(center_frequency_hz, type(center_frequency_hz)))
        if not isinstance(txop_timeout, TxOpTimeout):
            raise TxOpInitializationException(
                'txop_timeout must be an instance of type TxOpTimeout.\nvalue: {0}, type: {1}'.format(txop_timeout, type(txop_timeout)))
        if start_usec.value > stop_usec.value:
            raise TxOpInitializationException(
                'start_usec must be less than stop_usec.\nstart_usec: {0}, stop_usec: {1}'.format(
                    start_usec, stop_usec))

        self.start_usec = start_usec
        self.stop_usec = stop_usec
        self.center_frequency_hz = center_frequency_hz
        self.txop_timeout = txop_timeout
        self._rid = _rid

    def __str__(self):
        return 'start_usec: {0}, stop_usec: {1}, center_frequency_hz: {2}, txop_timeout: {3}, ' \
                '_rid: {4}'.format(self.start_usec,
                            self.stop_usec,
                            self.center_frequency_hz,
                            self.txop_timeout,
                            self._rid)
    __repr__ = __str__
