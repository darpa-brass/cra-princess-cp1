"""schedule_processor.py

Optimizes schedule based on constraints and channel bandwidth.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
import time
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.data_objects.processing.schedule import Schedule
from cp1.common.logger import Logger
from cp1.common.exception_class import InvalidAlgorithmException
from cp1.processing.schedule.algorithms.greedy import Greedy
from cp1.processing.schedule.algorithms.integer_program import IntegerProgram

logger = Logger().logger


class ScheduleProcessor:
    def __init__(self, constraints_object):
        """Constructs object and runs :func:`my text <cp1.processing.algorithm.preprocess()>`preprocess().

        :param ConstraintsObject constraints_object: The set of constraints on the schedule
                                   including the list of candidate TAs,
                                   available frequencies and new amount of
                                   available bandwidth
        """
        self.constraints_object = constraints_object
        self.schedule = Schedule(
            constraints_object.epoch, constraints_object.guard_band)

    def process(self, algorithm):
        """Optimizes across a set of TAs and constructs a schedule. Spare time allocated to first TA.

        :param Algorithm algorithm: Any algorithm, integer, greedy etc.
        :rtype: dict{Channel: List[TA]}
        """
        res = algorithm.optimize(constraints_object)
        schedule = res.schedule

        for channel, ta_list in schedule.items():
            channel.start_time = 0

            for ta in ta_list:
                one_way_transmission_length = (
                    ta.total_minimum_bandwidth.value / 2) / channel.num_partitions

                up_start = channel.start_time
                up_stop = one_way_transmission_length + channel.start_time
                down_start = up_stop + self.constraints_object.guard_band.value
                down_stop = down_start + one_way_transmission_length

                channel.start_time = down_stop + self.constraints_object.guard_band.value

                up_key = 'GR1_to_' + ta.id_.value
                down_key = ta.id_.value + '_to_GR1'

                for x in range(channel.num_partitions):
                    partition_offset = x * channel.partition_length
                    txop_up = TxOp(
                        start_usec=Microseconds(
                            (partition_offset + up_start) * 1000),
                        stop_usec=Microseconds(
                            (partition_offset + up_stop) * 1000),
                        center_frequency_hz=channel.frequency,
                        txop_timeout=self.constraints_object.txop_timeout)
                    txop_down = TxOp(
                        start_usec=Microseconds(
                            (partition_offset + down_start) * 1000),
                        stop_usec=Microseconds(
                            (partition_offset + down_stop) * 1000),
                        center_frequency_hz=channel.frequency,
                        txop_timeout=self.constraints_object.txop_timeout)

                    logger.info('Scheduled TxOp: Frequency: {0}, ID: {1}, StartUSec: {2}, StopUSec: {3}'.format(
                        channel.frequency.value, up_key, txop_up.start_usec.value, txop_up.stop_usec.value))
                    logger.info('Scheduled TxOp: Frequency: {0}, ID: {2}, StartUSec: {2}, StopUSec: {3}'.format(
                        channel.frequency.value, down_key, txop_down.start_usec.value, txop_down.stop_usec.value))
                    self.schedule.add(up_key, txop_up)
                    self.schedule.add(down_key, txop_down)
        return self.schedule
