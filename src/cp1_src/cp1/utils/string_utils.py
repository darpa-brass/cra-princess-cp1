"""string_utils.py

A set of functions to easily pretty format logging messages
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.algorithms.discretizers.accuracy_discretizer import AccuracyDiscretizer


# Logging offset counts. i.e. the number of characters in a DEBUG or INFO message intro.
# 2019-08-23 17:10:07,945 INFO = 29 characters
# 2019-08-23 17:10:07,945 DEBUG = 30 characters
INFO_LOG_OFFSET = 29
DEBUG_LOG_OFFSET = 30

# Logging messages upon completion and padding
PADDING = '****************************************************************'
HALF_PADDING = PADDING[:len(PADDING)//2]
start_message = '************** Commencing Challenge Problem 1... ***************'
end_message = '***************** Challenge Problem 1 Complete *****************'

def left_align_offset(x, offset_type=DEBUG_LOG_OFFSET):
    """Left aligns log outputs in relation to the type of logging message

    :param str x: The string to log
    :param int offset_type: The number of offsets, should be one of INFO_LOG_OFFSET or DEBUG_LOG_OFFSET
    :returns int: The amount to offset this log message by in order to left align it
    """
    return len(str(x)) + offset_type

def perturb_message(perturber):
    """Generates a pretty formatted perturber message

    :param Perturber perturber: The perturber used to perturb the solution
    """
    return '{0}\n{1}\n{2}\n{3}'.format(HALF_PADDING,
                               'Perturbing'.rjust(left_align_offset(str('Perturbing'))),
                               str(perturber).rjust(left_align_offset(str(perturber))),
                               HALF_PADDING.rjust(left_align_offset(HALF_PADDING)))

def instance_message(seed, discretizer, optimizer, scheduler):
    """Generates a pretty formatted completion message for an instance of a Challenge Problem

    :param str seed: The ConstraintsObject seed
    :param Discretizer discretizer: The Discretizer used in this instance
    :param Optimizer optimizer: The Optimizer used in this instance
    :param Scheduler scheduler: The Scheduler used in this instance
    :returns str: The pretty formatted logging message signalling the completion of an instance
    """
    if isinstance(discretizer, AccuracyDiscretizer):
        disc_write_val = discretizer.accuracy
    else:
        disc_write_val = discretizer.disc_count
    discretizer_log = '{0} ({1})'.format(discretizer, disc_write_val)

    seed_log = 'Seed {0}'.format(seed)

    return '{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(HALF_PADDING,
                                            seed_log.rjust(left_align_offset(seed_log)),
                                            discretizer_log.rjust(left_align_offset(discretizer_log)),
                                            str(optimizer).rjust(left_align_offset(optimizer)),
                                            str(scheduler).rjust(left_align_offset(scheduler)),
                                            HALF_PADDING.rjust(left_align_offset(HALF_PADDING)))

STARTING_MESSAGE = '{0}\n{1}\n{2}'.format(PADDING,
                                    start_message.rjust(left_align_offset(start_message)),
                                    PADDING.rjust(left_align_offset(PADDING)))

ENDING_MESSAGE = '{0}\n{1}\n{2}'.format(PADDING,
                                    end_message.rjust(left_align_offset(end_message)),
                                    PADDING.rjust(left_align_offset(PADDING)))