"""string_utils.py

A set of functions to easily pretty format logging messages
Author: Tameem Samawi (tsamawi@cra.com)
"""
from prettytable import PrettyTable
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
PADDING = '********************************************************************'
HALF_PADDING = PADDING[:len(PADDING) // 2]
_start_message = '**************** Commencing Challenge Problem 1... *****************'

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

def starting_message():
    return '{0}\n{1}\n{2}'.format(PADDING, center(_start_message),
                                center(PADDING))

def ending_message(total_runs, averages, config):
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
    def _create_tables(average):
        def format_table(table):
            # Apply center() to each row individually
            table_str = table.get_string()
            table_strs = table_str.split('\n')
            formatted_table = ''
            for x in table_strs:
                formatted_table += center(x + '\n')
            return formatted_table

        # Create table
        table = PrettyTable()
        table.title = average.type
        table.field_names = ['Metric', 'Lower Bound', 'CRA CP1', 'Upper Bound']

        # Populate rows
        table.add_row(['Number of TAs', average.lower_bound[0], average.cra_cp1[0], average.upper_bound[0]])
        table.add_row(['Solution Value', average.lower_bound[1], average.cra_cp1[1], average.upper_bound[1]])
        table.add_row(['Average Channel Efficiency', average.lower_bound[2], average.cra_cp1[2], average.upper_bound[2]])

        return format_table(table)

    message = ''
    end_message = '******************* Challenge Problem 1 Complete *******************'
    message += '{0}\n{1}\n'.format(PADDING, center(end_message))

    # Setup the tables
    tables = []
    for type, average in averages.averages.items():
        if config.perturb:
            if config.combine:
                if average.type == averages.COMBINED_PERTURBED_AVERAGE:
                    tables.append(_create_tables(average))
            else:
                if average.type == 'Minimum Bandwidth' and config.ta_bandwidth != 0:
                    tables.append(_create_tables(average))
                elif average.type == 'Channel Capacity' and config.channel_capacity != 0:
                    tables.append(_create_tables(average))
                elif average.type == 'Channel Dropoff' and config.channel_dropoff != 0:
                    tables.append(_create_tables(average))

        if average.type == averages.UNPERTURBED_AVERAGE:
            tables.append(_create_tables(average))
    for table in tables:
        message += table

    message += '{0}\n{1}\n'.format(center(PADDING), center(PADDING))
    return message
