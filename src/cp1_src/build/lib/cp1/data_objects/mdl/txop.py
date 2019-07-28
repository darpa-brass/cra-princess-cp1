"""txop.py

Data object representing a TxOp node.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from datetime import timedelta
from cp1.common.exception_class import TxOpInitializationException
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout


class TxOp:
    def __init__(
            self,
            ta,
            radio_link_id,
            start_usec,
            stop_usec,
            center_frequency_hz,
            txop_timeout,
            _rid=None):
            """
            Constructor

            :param TA ta: The TA this TxOp node is for
            :param str radio_link_id: The parent RadioLink's ID field so that this can be indexed into an OrientDB database
            :param datetime start_usec: The start transmission time in microseconds
            :param datetime stop_usec: The stop transmission time in microseconds
            :param Frequency center_frequency_hz: The frequency to communicate over
            :param TxOpTimeout txop_timeout: The timeout value
            """
            if not isinstance(start_usec, timedelta):
                raise TxOpInitializationException(
                    'start_usec ({0}) must be an instance of timedelta'.format(start_usec)
                )

            if not isinstance(stop_usec, timedelta):
                raise TxOpInitializationException(
                    'stop_usec ({0}) must be an instance of timedelta'.format(stop_usec)
                )

            if start_usec.microseconds >= stop_usec.microseconds:
                raise TxOpInitializationException(
                    'start_usec must be less than stop_usec.\nstart_usec: {0}, stop_usec: {1}'.format(
                        start_usec, stop_usec))

            self.ta = ta
            self.radio_link_id = radio_link_id
            self.start_usec = start_usec
            self.stop_usec = stop_usec
            self.center_frequency_hz = center_frequency_hz
            self.txop_timeout = txop_timeout
            self._rid = _rid

    def __str__(self):
        return 'radio_link_id: {0}, ' \
               'start_usec: {1}, ' \
               'stop_usec: {2}, ' \
               'center_frequency_hz: {3}, ' \
               'txop_timeout: {4}, ' \
               '_rid: {5}'.format(
                   self.radio_link_id,
                   self.start_usec,
                   self.stop_usec,
                   self.center_frequency_hz,
                   self.txop_timeout,
                   self._rid
               )

    def __eq__(self, other):
        if isinstance(other, TxOp):
            return (self.radio_link_id == other.radio_link_id and
                    self.stop_usec == other.stop_usec and
                    self.stop_usec == other.stop_usec and
                    self.center_frequency_hz == other.center_frequency_hz and
                    self.txop_timeout == other.txop_timeout and
                    self._rid == other._rid)
        return False

    __repr__ = __str__
