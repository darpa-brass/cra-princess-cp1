"""

schedule.py

Module to encapsulate optimizer output. Constructor is null because objects are added to the schedule as
they are generated.
Author: Tameem Samawi (tsamawi@cra.com)
"""

from cp1.data_objects.mdl.txop import TxOp
from cp1.common.exception_class import ScheduleInitializationException
from cp1.common.exception_class import InvalidScheduleException
from cp1.common.exception_class import ScheduleAddException
from cp1.data_objects.mdl.milliseconds import Milliseconds


class Schedule:
    def __init__(self, epoch, guard_band):
        if not isinstance(epoch, Milliseconds):
            raise ScheduleInitializationException(
                'epoch must be an instance of Milliseconds: {0}'.format(
                    epoch
                ), 'Schedule.__init__'
            )
        if not isinstance(guard_band, Milliseconds):
            raise ScheduleInitializationException(
                'guard_band must be an instance of Milliseconds: {0}'.format(
                    guard_band
                ), 'Schedule.__init__'
            )
        self.schedule = {}
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
            raise ScheduleAddException(
                'radio_link_key must be an instance of MdlId:\nvalue: {0}\ntype: {1}'.format(radio_link_key, type(radio_link_key)),
                'Schedule.add')
        if not isinstance(txop, TxOp):
            raise ScheduleAddException(
                'txop must be an instance of TxOp:\nvalue: {0}\ntype: {1}'.format(txop, type(txop)),
                'Schedule.add')

        # print('Adding txop: start {0} stop {1}'.format(txop.start_usec.value, txop.stop_usec.value))
        if not self.schedule:
                self.schedule = {radio_link_key: [txop]}  # Initialize
        else:
            if radio_link_key in self.schedule:
                self.schedule.get(radio_link_key).append(txop)
            else:
                self.schedule[radio_link_key] = [txop]

    def validate(self):
        for key in self.schedule:
            for txop in self.schedule[key]:
                if txop.start_usec.toSeconds() > self.epoch.toSeconds():
                    raise InvalidScheduleException(
                        'Schedule not allowed to exceed epoch. Found start time of: {0}'.format(txop.start_usec),
                        'Schedule.validate')
                elif txop.stop_usec.toSeconds() > self.epoch.toSeconds():
                    raise InvalidScheduleException(
                        'Schedule not allowed to exceed epoch. Found stop time of: {0}'.format(txop.stop_usec),
                        'Schedule.validate')
                elif txop.start_usec.toSeconds() < 0:
                    raise InvalidScheduleException(
                        'Negative start times not allowed. Found negative start time of: {0}'.format(txop.start_usec),
                        'Schedule.validate')
                elif txop.stop_usec.toSeconds() < 0:
                    raise InvalidScheduleException(
                        'Negative stop times not allowed. Found negative stop time of: {0}'.format(txop.stop_usec),
                        'Schedule.validate')
                elif txop.start_usec.toSeconds() > txop.stop_usec.toSeconds():
                    raise InvalidScheduleException(
                        'Start must be less than stop. Attempted to input a start time of: {0} stop time of: {1}'
                            .format(txop.start_usec, txop.stop_usec), 'Schedule.validate')
        return True

    def __str__(self):
        schedule_str = ''
        for k in self.schedule:
            txop_str = ''
            for txop in self.schedule[k]:
                txop_str += txop.__str__()
            schedule_str += '<Radio Link: {0}, TxOp Schedule: {1}>\n'.format(k, txop_str)
        return 'Schedule: {0}'.format(schedule_str)

    __repr__ = __str__
