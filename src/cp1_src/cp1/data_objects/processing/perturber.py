"""perturber.py

An object to handle perturbations to the original optimized solution.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import random
from copy import deepcopy
from cp1.data_objects.mdl.kbps import Kbps
from cp1.common.logger import Logger
from cp1.utils.string_utils import center

logger = Logger().logger


class Perturber:
    def __init__(
            self,
            reconsider=0,
            ta_bandwidth=0,
            channel_dropoff=0,
            channel_capacity=0,
            combine=0):
        """Constructor

        :param int reconsider: The number of additional TAs to
                                          reconsider after perturbing
        :param int ta_bandwidth: The amount by which to increase the bw
                                       of a TA by
        :param int channel_dropoff: If set to 1, will drop 1 scheduled TA from the
                                 channel it is currently scheduled on
        :param int channel_capacity: Increases a randomly selected channel's
                                            capacity by the amount specified.
                                            Can be negative.
        :param int combine: If set to 1, will run all perturbations once on instance.
        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        """
        self.reconsider = reconsider
        self.ta_bandwidth = ta_bandwidth
        self.channel_dropoff = channel_dropoff
        self.channel_capacity = channel_capacity
        self.combine = combine

    def perturb_constraints_object(self, constraints_object, optimizer_result):
        """Perturbs an optimization result based on the perturbations selected.
        There are three possible perturbations:
        1. If ta_bandwidth is set to any value other than 0, 1 random TA
        will have it's bandwidth value perturbed by the specified amount.
        2. If channel_dropoff is greater than 0, channel_dropoff number of TAs will be
        dropped from their channels until there are no TAs left to drop.
        3. If channel_capacity is set to any value other than 0, one random
        channel will have it's capacity increased or decreased by the specified
        amount.

        :param OptimizerResult optimizer_result: An unperturbed optimization result
        :returns OptimizerResult: A perturbed optimization result
        """
        # Increases the total_minimum_bandwidth value of a TA by the selected
        # amount in the ConfigurationObject
        unadapted_value = optimizer_result.value
        if self.ta_bandwidth != 0:
            ta_to_perturb = self._select_random_scheduled_ta(
                optimizer_result.scheduled_tas, constraints_object.seed)

            logger.debug('PERTURBATION: Changing {0} minimum bandwidth by {1}'.format(
                ta_to_perturb.id_, self._format_value(self.ta_bandwidth)))

            ta_to_perturb.total_minimum_bandwidth.value += self.ta_bandwidth
            ta_to_perturb.minimum_safety_bandwidth.value += (
                self.ta_bandwidth / 2)
            ta_to_perturb.minimum_voice_bandwidth.value += (
                self.ta_bandwidth / 2)
            ta_to_perturb.min_value = ta_to_perturb.compute_value_at_bandwidth(
                ta_to_perturb.total_minimum_bandwidth)

            # This is a workaround for the issue in floating point precision
            # in Python. Here I am setting the result to 0 if the two
            # floats are equal. Otherwise due to floating point precision
            # you get a value other than 0.
            if unadapted_value == ta_to_perturb.value:
                unadapted_value = 0
            else:
                unadapted_value -= ta_to_perturb.value

        # Randomly selects one channel to drop from the original
        # ConstraintsObject
        if self.channel_dropoff > 0:
            dropped_tas = []
            unadapted_value = optimizer_result.value
            for i in range(self.channel_dropoff):
                if len(dropped_tas) == len(optimizer_result.scheduled_tas):
                    logger.debug(
                        'All scheduled TAs have been dropped from their channels. The number of TAs you have requested to drop ({0}) has exceeded the amount of TAs that have been scheduled ({1}).'.format(
                            self.channel_dropoff, len(
                                optimizer_result.scheduled_tas)))
                    break

                else:
                    ta_to_perturb = self._select_random_scheduled_ta(
                        [ta for ta in optimizer_result.scheduled_tas if ta not in dropped_tas], constraints_object.seed)
                    dropped_tas.append(ta_to_perturb)
                    logger.debug(
                        'PERTURBATION: Removing {0} from {1}'.format(
                            ta_to_perturb.id_,
                            ta_to_perturb.channel.frequency.value))
                    ta_to_perturb.eligible_frequencies.remove(
                        ta_to_perturb.channel.frequency)

                    if unadapted_value == ta_to_perturb.value:
                        unadapted_value = 0
                    else:
                        unadapted_value -= ta_to_perturb.value
        # Increases or Decreases the capacity of one random channel
        if self.channel_capacity != 0:
            ta_to_perturb = self._select_random_scheduled_ta(
                optimizer_result.scheduled_tas, constraints_object.seed)
            channel_to_perturb = next(
                channel for channel in constraints_object.channels if channel == ta_to_perturb.channel)

            logger.debug(
                'PERTURBATION: Changing channel {0} capacity by {1}'.format(
                    ta_to_perturb.channel.frequency.value,
                    self._format_value(
                        self.channel_capacity)))
            channel_to_perturb.capacity.value += self.channel_capacity

            # In the case that the channel capacity is less than 0,
            # the algorithm should
            if self.channel_capacity < 0:
                logger.debug('Less than 0')
                original_len = len(optimizer_result.scheduled_tas)
                tas_on_perturbed_channel = [
                    ta for ta in optimizer_result.scheduled_tas if ta.channel == channel_to_perturb]
                tas_on_perturbed_channel.sort(
                    key=lambda x: x.bandwidth.value / x.value)

                total_bandwidth = sum(
                    ta.bandwidth.value for ta in tas_on_perturbed_channel)
                while channel_to_perturb.capacity.value < total_bandwidth:
                    ta = optimizer_result.scheduled_tas.pop()
                    unadapted_value -= ta.value
                    tas_on_perturbed_channel = [
                        ta for ta in optimizer_result.scheduled_tas if ta.channel == channel_to_perturb]
                    total_bandwidth = sum(
                        ta.bandwidth.value for ta in tas_on_perturbed_channel)

        # Randomly selects reconsider from the list of unscheduled TAs
        unscheduled_tas = [
            ta for ta in constraints_object.candidate_tas if ta.id_ not in [
                x.id_ for x in optimizer_result.scheduled_tas]]

        # The new candidate_tas for a ConstraintsObject is reconsider
        # unscheduled TAs and the scheduled TAs
        randomly_sampled_tas = []
        try:
            randomly_sampled_tas = random.sample(
                unscheduled_tas, self.reconsider)
        except ValueError:
            if len(unscheduled_tas) == 0:
                logger.debug(
                    """There are 0 unscheduled TAs to reconsider. The optimizer will attempt to resolve the perturbation using the currently scheduled TAs.""")
            else:
                logger.debug(
                    f"""The amount of TAs to reconsider ({self.reconsider}) is greater than the number of unscheduled TAs ({len(unscheduled_tas)}). Only able to reconsider {len(unscheduled_tas)} TA{'s' if len(unscheduled_tas) > 1 else ''}.""")
        # Reset the bandwidth and value assignments of TAs between runs
        for ta in optimizer_result.scheduled_tas:
            ta.value = 0
            ta.bandwidth = Kbps(0)

        scheduled_and_randomly_sampled_tas = optimizer_result.scheduled_tas + randomly_sampled_tas

        # Perturbed constraints objects are identical to original constraints,
        # just different candidate_tas and id
        constraints_object.id_ = 'Perturbed_{0}'.format(constraints_object.id_)
        constraints_object.candidate_tas = scheduled_and_randomly_sampled_tas

        return (constraints_object, unadapted_value)

    def _select_random_scheduled_ta(self, ta_list, seed):
        """Selects a randomly scheduled TA from an optimization result to perform a perturbation on.

        :param [TA] ta_list: The list from which to randonly select one scheduled TA
        :param int seed: Seeds the instance of random in this class
        :returns TA:
        """
        if seed != 'timestamp':
            random.seed(seed)

        random_scheduled_ta = random.choice(ta_list)
        return random_scheduled_ta

    def __str__(self):
        perturb_str = ''
        if self.channel_capacity != 0:
            perturb_str += '\n'
            perturb_str += center(
                'Channel Capacity {0}'.format(
                    self._format_value(
                        self.channel_capacity)))

        if self.channel_dropoff != 0:
            perturb_str += '\n'
            perturb_str += center(
                'Channel Dropoff {0}'.format(
                    self.channel_dropoff))

        if self.ta_bandwidth != 0:
            perturb_str += '\n'
            perturb_str += center(
                'Bandwidth Increase {0}'.format(
                    self._format_value(
                        self.ta_bandwidth)))

        return perturb_str

    def _format_value(self, x):
        if x > 0:
            sign = '+'
        else:
            sign = '-'
        return '{0}{1}'.format(sign, x)
