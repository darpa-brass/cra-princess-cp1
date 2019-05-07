"""txop.py

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
        return 'start_usec: {0}, ' \
               'stop_usec: {1}, ' \
               'center_frequency_hz: {2}, ' \
               'txop_timeout: {3}, ' \
               '_rid: {4}'.format(
                   self.start_usec,
                   self.stop_usec,
                   self.center_frequency_hz,
                   self.txop_timeout,
                   self._rid
               )

    def __eq__(self, other):
        if isinstance(other, TxOp):
            return (self.start_usec == other.start_usec and
                    self.stop_usec == other.stop_usec and
                    self.center_frequency_hz == other.center_frequency_hz and
                    self.txop_timeout == other.txop_timeout and
                    self._rid == other._rid)
        return False

    __repr__ = __str__
