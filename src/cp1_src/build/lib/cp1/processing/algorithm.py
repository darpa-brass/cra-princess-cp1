"""
algorithm.py

Optimizes schedule based on constraints and channel bandwidth.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import math
from cp1.common.logger import Logger
from cp1.data_objects.constraints.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.schedule import Schedule
from cp1.data_objects.mdl.microseconds import Microseconds
from cp1.common.exception_class import AlgorithmInitializationException

logger = Logger().logger


class Algorithm:
    def __init__(self, constraints_object):
        """
        Constructs object and runs :func:`my text <cp1.processing.algorithm.preprocess()>`preprocess().

        :param constraints_object: The set of constraints on the schedule
                                   including the list of candidate TAs,
                                   available frequencies and new amount of
                                   available bandwidth
        :type constraints_object: ConstraintsObject
        """
        if not isinstance(constraints_object, ConstraintsObject):
            raise AlgorithmInitializationException(
                'constraints_object must be instance of ConstraintsObject: {0}'.format(constraints_object),
                'Algorithm.__init__')
        self.constraints_object = constraints_object
        self.schedule = Schedule(
            constraints_object.epoch,
            constraints_object.guard_band)
        self.preprocess()

        logger.info('Scheduling TAs in the following order:')
        #   Print out TA's in order based on utility threshold ratio
        for ta in self.constraints_object.candidate_tas:
            logger.info(ta)


    def optimize(self):
        """
        Creates a new schedule based on updated bandwidth availability, channel
        frequency and TAs seeking to join the network.

        :returns bool: dict<str, List[MDLTxOp]>
        """
        self.determine_eligible_tas()
        self.schedule_eligible_tas()

        # Compute total utility
        sum = 0
        for ta in self.eligible_tas:
            sum += ta.utility_threshold
        logger.info('Total value in new schedule is: {0}'.format(sum))

        return self.schedule.schedule

    def determine_eligible_tas(self):
        """
        Checks which TAs in the list of candidate_tas can be scheduled. Adds
        any TAs that can fit to self.eligible_tas. Also computes the spare
        time left in each partition. This spare time should be scheduled in
        so that there is no wasted time in the new schedule.
        A TA requires the total_minimum_bandwidth and twice the guard band
        since TAs require two-way communication; Ground to TA and TA to Ground.
        """
        first_available_time = 0
        for ta in self.constraints_object.candidate_tas:
            bandwidth_requirement = (
            ta.total_minimum_bandwidth.value / self.num_partitions) + (
            2 * self.constraints_object.guard_band.value)

            if bandwidth_requirement + first_available_time <= self.partition_length:
                first_available_time += bandwidth_requirement
                self.eligible_tas.append(ta)
                logger.info('{0} selected for scheduling'.format(ta.id_))

        self.spare_time = self.partition_length - first_available_time

    def schedule_eligible_tas(self):
        """
        Calculates transmission times and adds TxOp nodes to the schedule.
        The first TA that is scheduled will be allocated all spare time in
        (the very likely) case TA's do not schedule perfectly.
        """
        for ta in self.eligible_tas:
            one_way_transmission_length = (ta.total_minimum_bandwidth.value / 2) / self.num_partitions
            if ta.id_ == self.eligible_tas[0].id_:
                one_way_transmission_length += (self.spare_time / 2)

            up_start = self.first_available_time
            up_stop = one_way_transmission_length + self.first_available_time
            down_start = up_stop + self.constraints_object.guard_band.value
            down_stop = down_start + one_way_transmission_length


            self.first_available_time = down_stop + self.constraints_object.guard_band.value

            up_key = 'GR1_to_' + ta.id_.value
            down_key = ta.id_.value + '_to_GR1'
            for x in range(self.num_partitions):
                partition_offset = x * self.partition_length

                txop_up = TxOp(
                    start_usec=Microseconds(
                    (partition_offset + up_start) * 1000),
                    stop_usec=Microseconds(
                    (partition_offset + up_stop) * 1000),
                    center_frequency_hz=self.constraints_object.channel.frequency,
                    txop_timeout=self.constraints_object.channel.timeout)

                txop_down = TxOp(
                    start_usec=Microseconds(
                        (partition_offset + down_start) * 1000),
                    stop_usec=Microseconds(
                        (partition_offset + down_stop) * 1000),
                    center_frequency_hz=self.constraints_object.channel.frequency,
                    txop_timeout=self.constraints_object.channel.timeout)

                logger.info('Adding TxOp node: ID: {0}, StartUSec: {1}, StopUSec: {2}'.format(up_key, txop_up.start_usec.value, txop_up.stop_usec.value))
                logger.info('Adding TxOp node: ID: {0}, StartUSec: {1}, StopUSec: {2}'.format(down_key, txop_down.start_usec.value, txop_down.stop_usec.value))
                self.schedule.add(up_key, txop_up)
                self.schedule.add(down_key, txop_down)

    def preprocess(self):
        """
        Sets first available time to 0
        Sorts candidate TAs by the ratio of their utility to minimum
        bandwidth requirement
        Calculates the number of partitions
        Computes the length of each partition
        """
        self.eligible_tas = []
        self.first_available_time = 0

        self.constraints_object.candidate_tas.sort(
        key=lambda ta: (ta.utility_threshold / ta.total_minimum_bandwidth.value), reverse=True)

        if self.constraints_object.latency.value == 0:
            self.num_partitions = 1
        else:
            self.num_partitions = math.ceil(
                self.constraints_object.epoch.value /
                self.constraints_object.latency.value)

        self.partition_length = self.constraints_object.epoch.value / self.num_partitions

    # def print_new_schedule(self):
    #     txop_list = []
    #     for ta in self.schedule.schedule:
    #         txop_list.append(self.schedule.schedule.get(ta))
