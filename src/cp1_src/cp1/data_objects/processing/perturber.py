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

    def perturb_constraints_object(self, constraints_object, optimizer_result, lower_bound_optimizer_result):
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
        :param OptimizerResult lower_bound_optimizer_result: The result of the lower bound optimizaztion to use when computing averages
        :returns OptimizerResult: A perturbed optimization result
        """
        optimizer_result = deepcopy(optimizer_result)
        lower_bound_optimizer_result = deepcopy(lower_bound_optimizer_result)
        # Increases the total_minimum_bandwidth value of a TA by the selected
        # amount in the ConfigurationObject
        if self.ta_bandwidth != 0:
            for or_ in [lower_bound_optimizer_result, optimizer_result]:
                ta_to_perturb = self._select_random_scheduled_ta(
                    or_.scheduled_tas, constraints_object.seed)

                if or_ == optimizer_result:
                    logger.debug('PERTURBATION: Changing {0} minimum bandwidth by {1}'.format(
                        ta_to_perturb.id_, self.ta_bandwidth))

                if ta_to_perturb.total_minimum_bandwidth.value - self.ta_bandwidth < 0:
                    self.ta_bandwidth = ta_to_perturb.total_minimum_bandwidth.value

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
                if or_ == lower_bound_optimizer_result:
                    if lower_bound_optimizer_result.value == ta_to_perturb.value:
                        lower_bound_optimizer_result.value = 0
                        lower_bound_optimizer_result.scheduled_tas = []
                    else:
                        lower_bound_optimizer_result.value -= ta_to_perturb.value
                        lower_bound_optimizer_result.scheduled_tas.remove(ta_to_perturb)
                        for channel, ta_list in lower_bound_optimizer_result.scheduled_tas_by_channel.items():
                            for ta in ta_list:
                                if ta == ta_to_perturb:
                                    ta_list.remove(ta)
        # Randomly selects one channel to drop from the original
        # ConstraintsObject
        if self.channel_dropoff > 0:
            for or_ in [lower_bound_optimizer_result, optimizer_result]:
                dropped_tas = []
                for i in range(self.channel_dropoff):
                    if len(dropped_tas) == len(or_.scheduled_tas):
                        logger.debug(
                            'All scheduled TAs have been dropped from their channels. The number of TAs you have requested to drop ({0}) has exceeded the amount of TAs that have been scheduled ({1}).'.format(
                                self.channel_dropoff, len(
                                    or_.scheduled_tas)))
                        break

                    else:
                        ta_to_perturb = self._select_random_scheduled_ta(
                            [ta for ta in or_.scheduled_tas if ta not in dropped_tas], constraints_object.seed)
                        dropped_tas.append(ta_to_perturb)
                        if or_ == optimizer_result:
                            logger.debug(
                                'PERTURBATION: Removing {0} from {1}'.format(
                                    ta_to_perturb.id_,
                                    ta_to_perturb.channel.frequency.value))
                            ta_to_perturb.eligible_frequencies.remove(
                                ta_to_perturb.channel.frequency)

                if or_ == lower_bound_optimizer_result:
                    previously_scheduled_tas = deepcopy(or_.scheduled_tas)
                    or_.scheduled_tas = [ta for ta in previously_scheduled_tas if ta not in dropped_tas]
                    for channel, ta_list in or_.scheduled_tas_by_channel.items():
                        old_ta_list = deepcopy(ta_list)
                        or_.scheduled_tas_by_channel[channel] = [ta for ta in old_ta_list if ta not in dropped_tas]
                    or_.value = sum([ta.value for ta in or_.scheduled_tas])
        # Increases or Decreases the capacity of one random channel
        if self.channel_capacity != 0:
            for or_ in [lower_bound_optimizer_result, optimizer_result]:
                ta_to_perturb = self._select_random_scheduled_ta(
                    or_.scheduled_tas, constraints_object.seed)
                channel_to_perturb = next(
                    channel for channel in constraints_object.channels if channel == ta_to_perturb.channel)

                if or_ == optimizer_result:
                    logger.debug(
                        'PERTURBATION: Changing channel {0} capacity by {1}'.format(
                            ta_to_perturb.channel.frequency.value,
                                self.channel_capacity))
                channel_to_perturb.capacity.value += self.channel_capacity

                    # If the amount of bandwidth to reduce the channel by exceeds the
                    # channel's capacity. Remove that channel, an the scheduled TAs on it.
                if channel_to_perturb.capacity.value <= 0:
                    for ta in or_.scheduled_tas:
                        tas_to_remove = []
                        if ta.channel.frequency.value == channel_to_perturb.frequency.value:
                            tas_to_remove.append(ta)
                            or_.value -= ta.value
                    for channel, ta_list in or_.scheduled_tas_by_channel.items():
                        if channel == channel_to_perturb:
                            or_.scheduled_tas_by_channel[channel] = []
                    constraints_object.channels.remove(channel_to_perturb)

                    previously_scheduled_tas = deepcopy(or_.scheduled_tas)
                    or_.scheduled_tas = [ta for ta in previously_scheduled_tas if ta not in tas_to_remove]
                    # Update the value if you're dealing with a greedy optimization
                    if or_ == lower_bound_optimizer_result:
                        or_.value = sum([ta.value for ta in or_.scheduled_tas])

                if or_ == lower_bound_optimizer_result:
                    if self.channel_capacity < 0:
                        tas_to_remove = []
                        for ta in or_.scheduled_tas:
                            if ta.channel.frequency.value == channel_to_perturb.frequency.value:
                                tas_to_remove.append(ta)
                                or_.value -= ta.value
                        for channel, ta_list in or_.scheduled_tas_by_channel.items():
                            if channel == channel_to_perturb:
                                or_.scheduled_tas_by_channel[channel] = []

                        previously_scheduled_tas = deepcopy(or_.scheduled_tas)
                        or_.scheduled_tas = [ta for ta in previously_scheduled_tas if ta not in tas_to_remove]
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
        constraints_object.candidate_tas = scheduled_and_randomly_sampled_tas

        # Just in case the perturbations have sent this value beneath 0
        if lower_bound_optimizer_result.value < 0:
            lower_bound_optimizer_result.value = 0
        if len(lower_bound_optimizer_result.scheduled_tas) < 0:
            lower_bound_optimizer_result.scheduled_tas = []

        return (constraints_object, lower_bound_optimizer_result)

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
                'Channel Capacity {0}'.format(self.channel_capacity))

        if self.channel_dropoff != 0:
            perturb_str += '\n'
            perturb_str += center(
                'Channel Dropoff {0}'.format(self.channel_dropoff))

        if self.ta_bandwidth != 0:
            perturb_str += '\n'
            perturb_str += center(
                'TA Minimum Bandwidth {0}'.format(self.ta_bandwidth))

        return perturb_str
