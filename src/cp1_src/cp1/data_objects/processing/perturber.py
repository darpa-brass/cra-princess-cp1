"""perturber.py

An object to handle perturbations to the original optimized solution.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import random
from copy import deepcopy
from cp1.data_objects.mdl.kbps import Kbps
from cp1.common.logger import Logger

logger = Logger().logger


class Perturber:
    def __init__(self, num_tas_to_reconsider=0, increase_ta_min_bw=0, drop_channel=0, change_channel_capacity=0, seed=None):
        """Constructor

        :param int num_tas_to_reconsider: The number of additional TAs to
                                          reconsider after perturbing
        :param int increase_ta_min_bw: The amount by which to increase the bw
                                       of a TA by
        :param int drop_channel: If set to 1, will drop 1 scheduled TA from the
                                 channel it is currently scheduled on
        :param int change_channel_capacity: Increases a randomly selected channel's
                                            capacity by the amount specified.
                                            Can be negative.
        :param int seed: If none, will not seed. Otherwise set to value passed in.
        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        """
        self.num_tas_to_reconsider = num_tas_to_reconsider
        self.increase_ta_min_bw = increase_ta_min_bw
        self.drop_channel = drop_channel
        self.change_channel_capacity = change_channel_capacity
        self.seed = seed

    def perturb_constraints_object(self, constraints_object, optimizer_result):
        """Perturbs an optimization result based on the perturbations selected.
        There are three possible perturbations:
        1. If increase_ta_min_bw is set to any value other than 0, 1 random TA
        will have it's bandwidth value perturbed by the specified amount.
        2. If drop_channel is set to 1, one randomly selected TA will be dropped
        from its current channel
        3. If change_channel_capacity is set to any value other than 0, one random
        channel will have it's capacity increased or decreased by the specified
        amount.

        :param OptimizerResult optimizer_result: An unperturbed optimization result
        :returns OptimizerResult: A perturbed optimization result
        """
        # Increases the total_minimum_bandwidth value of a TA by the selected
        # amount in the ConfigurationObject
        if self.increase_ta_min_bw != 0:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            ta_to_perturb.total_minimum_bandwidth.value += self.increase_ta_min_bw
            ta_to_perturb.minimum_safety_bandwidth.value += (self.increase_ta_min_bw / 2)
            ta_to_perturb.minimum_voice_bandwidth.value += (self.increase_ta_min_bw / 2)
            ta_to_perturb.min_value = ta_to_perturb.compute_value_at_bandwidth(ta_to_perturb.total_minimum_bandwidth)
            logger.debug('Increasing {0} minimum bandwidth by {1}'.format(ta_to_perturb.id_, self.increase_ta_min_bw))

        # Randomly selects one channel to drop from the original ConstraintsObject
        if self.drop_channel == 1:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            for i in range(len(ta_to_perturb.eligible_frequencies)):
                if ta_to_perturb.channel == constraints_object.channels[i]:
                    logger.debug('Removing {0} from {1}'.format(ta_to_perturb.id_, ta_to_perturb.channel.frequency.value))
                    ta_to_perturb.eligible_frequencies.pop(i)
                    break

        # Increases or Decreases the capacity of one random channel
        if self.change_channel_capacity != 0:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            for i in range(len(constraints_object.channels)):
                if ta_to_perturb.channel == constraints_object.channels[i]:
                    constraints_object.channels[i].capacity.value += self.change_channel_capacity
                    logger.debug('Changing channel {0} capacity by {1}'.format(ta_to_perturb.channel.frequency.value, self.change_channel_capacity))
                    break

        # Randomly selects num_tas_to_reconsider from the list of unscheduled TAs
        unscheduled_tas = [ta for ta in constraints_object.candidate_tas if ta.id_ not in [x.id_ for x in optimizer_result.scheduled_tas]]

        # The new candidate_tas for a ConstraintsObject is num_tas_to_reconsider
        # UNSCHEDULED TAs and the scheduled TAs
        tas_to_reconsider = []
        if unscheduled_tas:
            tas_to_reconsider = random.sample(unscheduled_tas, self.num_tas_to_reconsider)

        scheduled_and_randomly_sampled_tas = []
        for ta in optimizer_result.scheduled_tas:
            ta.value = 0
            ta.bandwidth = Kbps(0)
        scheduled_and_randomly_sampled_tas = tas_to_reconsider + optimizer_result.scheduled_tas

        # Perturbed constraints objects are identical to original constraints, just different candidate_tas and id
        constraints_object.id_ = 'Perturbed_{0}'.format(constraints_object.id_)
        constraints_object.candidate_tas = scheduled_and_randomly_sampled_tas

        return constraints_object

    def _select_random_scheduled_ta(self, optimizer_result):
        """Selects a randomly scheduled TA from an optimization result to perform a perturbation on.

        :param OptimizerResult optimizer_result: The result from which to randonly select one scheduled TA
        :returns TA:
        """
        if self.seed is not None:
            random.seed(self.seed)

        random_scheduled_ta = random.choice(optimizer_result.scheduled_tas)
        return random_scheduled_ta

    def __str__(self):
        perturb_str = ''
        if self.change_channel_capacity != 0:
            perturb_str = 'Change_Channel_Capacity_{0}'.format(self.change_channel_capacity)

        if self.drop_channel != 0:
            perturb_str = 'Drop_Channel_{0}'.format(self.drop_channel)

        if self.increase_ta_min_bw != 0:
            perturb_str = 'Increase_TA_Min_Bandwidth_{0}'.format(self.increase_ta_min_bw)

        return perturb_str
