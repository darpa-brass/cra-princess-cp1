"""

schedule.py

Module to encapsulate optimizer output. Constructor is null because objects are added to the schedule as
they are generated.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.data_objects.mdl.txop import TxOp
from cp1.common.exception_class import ScheduleInitializationError
from cp1.common.exception_class import InvalidScheduleError
from cp1.common.exception_class import ScheduleAddError
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.mdl.microseconds import Microseconds


class Schedule:
    def __init__(self, epoch, guard_band):
        if not isinstance(epoch, Milliseconds):
            raise ScheduleInitializationError(
                'epoch must be an instance of Milliseconds: {0}'.format(
                    epoch
                ), 'Schedule.__init__'
            )
        if not isinstance(guard_band, Microseconds):
            raise ScheduleInitializationError(
                'guard_band must be an instance of Microseconds: {0}'.format(
                    guard_band
                ), 'Schedule.__init__'
            )
        self.schedule = None
        self.epoch = epoch
        self.guard_band = guard_band

    def add(self, radio_link_key, txop):
        """
        Adds a new schedule for a specific RadioLink connection

        :param txop: A TxOp node
        :type txop: MDLTxOp

        :param radio_link_key: RadioLink ID of current schedule
        :type radio_link_key: str
        """
        if not isinstance(radio_link_key, str):
            raise ScheduleAddError(
                'radio_link_key must be an instance of str: {0}'.format(radio_link_key),
                'Schedule.add')
        if not isinstance(txop, TxOp):
            raise ScheduleAddError(
                'txop must be an instance of TxOp: {0}'.format(txop),
                'Schedule.add')

        if self.schedule is None:
            self.schedule = {radio_link_key: [txop]}
            print('Adding txop: start {0} stop {1}'.format(txop.start_usec.value, txop.stop_usec.value))
        else:
            if radio_link_key in self.schedule:
                # if self.validate(txop):
                self.schedule.get(radio_link_key).append(txop)
                print('New transmission generated txop: start {0} stop {1}'.format(txop.start_usec.value, txop.stop_usec.value))
            else:
                self.schedule[radio_link_key] = [txop]

    def validate(self, curr_txop):
        if curr_txop.stop_usec.toSeconds() > self.epoch.toSeconds():
            raise InvalidScheduleError(
                'Schedule not allowed to exceed epoch: {0}'.format(curr_txop),
                'Schedule.validate')
        elif curr_txop.start_usec.toSeconds() < 0 or curr_txop.stop_usec.toSeconds() < 0:
            raise InvalidScheduleError(
                'Negative start or stop times not allowed: {0}'.format(curr_txop),
                'Schedule.validate')
        elif curr_txop.start_usec.toSeconds() > curr_txop.stop_usec.toSeconds():
            raise InvalidScheduleError(
                'Start must be less than stop: {0}'.format(curr_txop),
                'Schedule.validate')
        else:
            latest_time = 0
            for x in self.schedule:
                for txop in self.schedule[x]:
                    if txop.stop_usec.value > latest_time:
                        latest_time = txop.stop_usec.value

            if curr_txop.start_usec.value - self.guard_band.value != latest_time:
                raise InvalidScheduleError(
                    'Start time is too far after last recorded time. Last recorded time: {0}, '
                    'start time: {1}, guard band: {2}'.format(
                        latest_time, curr_txop.start_usec, self.guard_band))

