"""perturber.py

An object to handle perturbations to the original optimized solution.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import random
from copy import deepcopy


class Perturber:
    def __init__(self, config):
        """Constructor
        :param ConfigurationObject config: The Configuration for an instance of a challenge problem
        """
        self.num_tas_to_reconsider = config.num_tas_to_reconsider
        self.increase_ta_min_bw = config.increase_ta_min_bw
        self.drop_channel = config.drop_channel
        self.change_channel_capacity = config.change_channel_capacity

    def perturb_constraints_object(self, constraints_object, optimizer_result):
        """Perturbs an optimization result based on the perturbations selected

        :param OptimizerResult optimizer_result: An unperturbed optimization result
        :returns OptimizerResult: A perturbed optimization result
        """
        # Increases the total_minimum_bandwidth value of a TA by the selected
        # amount in the ConfigurationObject
        if self.increase_ta_min_bw > 0:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            ta_to_perturb.total_minimum_bandwidth.value += self.increase_ta_min_bw

        # Randomly selects one channel to drop from the original ConstraintsObject
        if self.drop_channel == 1:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            for i in range(len(ta_to_perturb.eligible_channels)):
                if ta_to_perturb.channel.frequency == ta_to_perturb.eligible_frequencies[i]:
                    ta_to_perturb.eligible_channels.pop(i)
                    break

        # Increases or Decreases the capacity of one random channel
        if self.change_channel_capacity != 0:
            ta_to_perturb = self._select_random_scheduled_ta(optimizer_result)
            ta_to_perturb.channel.capacity.value += self.change_channel_capacity

        # Randomly selects num_tas_to_reconsider from the list of unscheduled TAs
        unscheduled_tas = [ta for ta in constraints_object.candidate_tas if ta.id_ not in [x.id_ for x in optimizer_result.scheduled_tas_list]]

        # The new candidate_tas for a ConstraintsObject is num_tas_to_reconsider
        # UNSCHEDULED TAs and the scheduled TAs
        tas_to_reconsider = random.sample(unscheduled_tas, self.num_tas_to_reconsider)
        scheduled_and_randomly_sampled_tas = tas_to_reconsider + optimizer_result.scheduled_tas_list

        # Perturbed constraints objects are identical to original constraints, just different candidate_tas and id
        perturbed_constraints_object = deepcopy(constraints_object)
        perturbed_constraints_object.id_ = 'Perturbed_{0}'.format(constraints_object.id_)
        perturbed_constraints_object.candidate_tas = scheduled_and_randomly_sampled_tas

        return perturbed_constraints_object

    def _select_random_scheduled_ta(self, optimizer_result):
        """Selects a randomly scheduled TA from an optimization result to perform a perturbation on.

        :param OptimizerResult optimizer_result: The result from which to randonly select one scheduled TA
        :returns TA:
        """
        random_scheduled_ta = random.choice(optimizer_result.scheduled_tas_list)
        return random_scheduled_ta
