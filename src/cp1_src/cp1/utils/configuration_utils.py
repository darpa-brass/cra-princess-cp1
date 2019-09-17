"""configuration_utils.py

Utilities to set up algorithms based on a ConfigurationObject.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.algorithms.discretizers.accuracy_discretizer import AccuracyDiscretizer
from cp1.algorithms.discretizers.bandwidth_discretizer import BandwidthDiscretizer
from cp1.algorithms.discretizers.value_discretizer import ValueDiscretizer
from cp1.algorithms.optimizers.integer_program import IntegerProgram
from cp1.algorithms.optimizers.dynamic_program import DynamicProgram
from cp1.algorithms.optimizers.greedy_optimizer import GreedyOptimizer
from cp1.algorithms.optimizers.gurobi import Gurobi
from cp1.algorithms.schedulers.conservative_scheduler import ConservativeScheduler
from cp1.algorithms.schedulers.hybrid_scheduler import HybridScheduler
from cp1.data_objects.processing.perturber import Perturber


def setup_perturbers(config):
    """Sets up an array of Perturbers based on config settings.
    One Perturber object is created per perturbation field.

    :param ConfigurationObject config: The Configuration for an instance of a challenge problem
    :returns [<Scheduler>] schedulers: A list of schedulers based on the configuration object values
    """
    perturbers = []
    if config.perturb == 1:

        if config.increase_ta_min_bw != 0:
            perturbers.append(Perturber(
            num_tas_to_reconsider = config.num_tas_to_reconsider,
            increase_ta_min_bw = config.increase_ta_min_bw))

        if config.drop_channel != 0:
            perturbers.append(Perturber(
            num_tas_to_reconsider = config.num_tas_to_reconsider,
            drop_channel = config.drop_channel))

        if config.change_channel_capacity != 0:
            perturbers.append(Perturber(
            num_tas_to_reconsider = config.num_tas_to_reconsider,
            change_channel_capacity = config.change_channel_capacity))

    for perturber in perturbers:
        if config.testing == 1:
            if config.testing_seed != 'timestamp':
                perturber.seed = config.testing_seed
        elif len(config.instances) == 2:
            perturber.seed = config.instances[1]

    return perturbers

def setup_schedulers(config):
    """Sets up an array of Schedulers based on config settings.
    :param ConfigurationObject config: The Configuration for an instance of a challenge problem
    :returns [<Scheduler>] schedulers: A list of schedulers based on the configuration object values
    """
    schedulers = []
    if config.conservative == 1:
        schedulers.append(ConservativeScheduler())
    if config.hybrid == 1:
        schedulers.append(HybridScheduler())
    return schedulers

def setup_discretizers(config):
    """Sets up an array of Discretizers based on config settings.
    :param ConfigurationObject config: The Configuration for an instance of a challenge problem
    :returns [<Discretizer>] discretizers: A list of Discretizer objects, one per discretization value passed into the discretization array
    """
    discretizers = []
    for x in config.accuracy_epsilons:
        discretizers.append(AccuracyDiscretizer(x))
    for x in config.bandwidth_discs:
        discretizers.append(BandwidthDiscretizer(x))
    for x in config.value_discs:
        discretizers.append(ValueDiscretizer(x))
    return discretizers

def setup_optimizers(config):
    """Sets up an array of Optimizers based on config settings.
    :param ConfigurationObject config: The Configuration for an instance of a challenge problem
    :returns [<Optimizers>] optimizers: A list of optimizers, one per confiuration setting passed in
    """
    optimizers = []
    if config.cbc == 1:
        optimizers.append(IntegerProgram())
    if config.gurobi == 1:
        optimizers.append(Gurobi())
    if config.dynamic == 1:
        optimizers.append(DynamicProgram())
    if config.greedy == 1:
        optimizers.append(GreedyOptimizer())
    return optimizers
