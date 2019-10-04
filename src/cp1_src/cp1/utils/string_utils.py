"""string_utils.py

A set of functions to easily pretty format logging messages
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.algorithms.discretizers.accuracy_discretizer import AccuracyDiscretizer
from cp1.common.logger import Logger

logger = Logger().logger

# Logging offset counts. i.e. the number of characters in a DEBUG or
# INFO message intro.
# 2019-08-23 17:10:07,945 INFO = 29 characters
# 2019-08-23 17:10:07,945 DEBUG = 30 characters
INFO_LOG_OFFSET = 29
DEBUG_LOG_OFFSET = 30

# Logging messages upon completion and padding
PADDING = '****************************************************************'
HALF_PADDING = PADDING[:len(PADDING) // 2]
_start_message = '************** Commencing Challenge Problem 1... ***************'

def center(x, offset_type=DEBUG_LOG_OFFSET):
    """Left aligns log outputs in relation to the type of logging
       message

    :param str x: The string to log
    :param int offset_type: The number of offsets, should be one of
                            INFO_LOG_OFFSET or DEBUG_LOG_OFFSET
    :returns int: The amount to offset this log message by in order to
                  left align it
    """
    return str(x).rjust(len(str(x)) + offset_type)

def perturb_message(perturber):
    """Generates a pretty formatted perturber message

    :param Perturber perturber: The perturber used to perturb the solution
    """
    return '{0}\n{1}\n{2}\n{3}'.format(
        HALF_PADDING,
        center('Perturbing'),
        (str(perturber)),
        center(HALF_PADDING))

def instance_message(run, seed, discretizer, optimizer, scheduler):
    """Generates a pretty formatted completion message for an instance
       of a Challenge Problem.

    :param int run: The run number. i.e. ID of the ConstraintsObject.
    :param str seed: The ConstraintsObject seed
    :param Discretizer discretizer: The Discretizer used in this
                                    instance
    :param Optimizer optimizer: The Optimizer used in this instance
    :param Scheduler scheduler: The Scheduler used in this instance
    :returns str: The pretty formatted logging message signalling the
                  completion of an instance
    """
    return '{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}'.format(
        HALF_PADDING,
        center('Run {0}'.format(run)),
        center('Seed {0}'.format(seed)),
        center(discretizer),
        center(optimizer),
        center(scheduler),
        center(HALF_PADDING))

def ending_message(total_runs, averages, perturb=False, combined=False):
    """Returns a report of the average gain by perturbation

    :param int total_runs: The total number of runs
    :param {str: [int]} averages: A dictionary whereby the key is the
                                  averate type i.e. `Optimized` and the
                                  value is the average value for that
                                  type i.e. 495. For the three types of
                                  perturbations, this is represented as
                                  a list, whereby the first value in the
                                  list represents the average value for
                                  the solutions before the perturbation
                                  was applied, the second value in the
                                  list represents the value after the
                                  perturbation is applied when using
                                  our framework (we call this
                                  'adapting'), and the third value
                                  represents the solution after the
                                  perturbation is applied, but without
                                  adapting.
    :param boolean combined: Whether or not these perturbations were run
                             in combination. This determines whether to
                             print 3 seperate reports for a perturbation
                             or just one, combined report.
    """
    end_message = '***************** Challenge Problem 1 Complete *****************'
    message = '{0}\n{1}\n'.format(PADDING, center(end_message))
    for average_type, average_value in averages.items():
        if isinstance(average_value, list):
            if perturb:
                if combined:
                    if average_type == 'Perturbations':
                        message += center('{0} {1}\n'.format(average_type, average_value))
                else:
                    if average_type != 'Perturbations':
                        message += center('{0} {1}\n'.format(average_type, average_value))
        else:
            message += center('{0} {1}\n'.format(average_type, average_value))
    message += '{0}\n{1}\n'.format(center(PADDING), center(PADDING))
    return message

STARTING_MESSAGE = '{0}\n{1}\n{2}'.format(PADDING,
                                         center(_start_message),
                                         center(PADDING))
