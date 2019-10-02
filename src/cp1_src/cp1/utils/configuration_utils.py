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
        if config.combine == 1:
            perturbers.append(Perturber(
            reconsider = config.reconsider,
            ta_bandwidth = config.ta_bandwidth,
            channel_dropoff = config.channel_dropoff,
            channel_capacity = config.channel_capacity))

        else:
            if config.ta_bandwidth != 0:
                perturbers.append(Perturber(
                reconsider = config.reconsider,
                ta_bandwidth = config.ta_bandwidth))

            if config.channel_dropoff != 0:
                perturbers.append(Perturber(
                reconsider = config.reconsider,
                channel_dropoff = config.channel_dropoff))

            if config.channel_capacity != 0:
                perturbers.append(Perturber(
                reconsider = config.reconsider,
                channel_capacity = config.channel_capacity))

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
    for x in config.accuracy:
        discretizers.append(AccuracyDiscretizer(x))
    for x in config.bandwidth:
        discretizers.append(BandwidthDiscretizer(x))
    for x in config.value:
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
    if config.dynamic == 1:
        optimizers.append(DynamicProgram())
    if config.greedy == 1:
        optimizers.append(GreedyOptimizer())
    return optimizers
