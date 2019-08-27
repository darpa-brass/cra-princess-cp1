import os
from cp1.common.logger import Logger
from cp1.data_objects.constants.constants import *

logger = Logger()
logger.setup_file_handler(os.path.abspath(LOGGING_DIR))
logger = logger.logger

import time
from copy import deepcopy
from cp1.utils.decorators.timedelta import timedelta
from brass_mdl_tools.mdl_generator import generate_mdl_shell
from cp1.utils.file_utils import *
from cp1.utils.string_utils import *
from cp1.data_objects.constants.constants import *
from cp1.utils.configuration_utils import *
from cp1.utils.constraints_object_generator import *
from cp1.data_objects.processing.configuration_object import ConfigurationObject
from cp1.algorithms.optimizers.integer_program import IntegerProgram
from cp1.data_objects.processing.perturber import Perturber


def solve_challenge_problem_instance(constraints_object, discretizer, optimizer, scheduler, perturb_optimizer_result=None):
    """Runs through all steps required to solve a challenge problem instance.

    :param ConstraintsObject constraints_object: A Constraints Object containing all data necessary to optimize over.
    :param Discretizer discretizer: The discretizer algorithm to use when discretizing TAs
    :param Optimizer optimizer: The optimizer algorithm to use when optimizing TAs
    :param Scheduler scheduler: The scheduler algorithm to use when scheduling TAs
    :param OptimizerResult perturb: The OptimizerResult to perturb
    """
    ub_constraints_object = deepcopy(constraints_object)

    if perturb_optimizer_result is not None:
        logger.debug('Perturbing Constraints Object...')
        constraints_object = perturber.perturb_constraints_object(constraints_object, perturb_optimizer_result)

    logger.debug('Discretizing TAs...')
    discretized_tas = discretizer.discretize(constraints_object)

    logger.debug('Optimizing Constraints Object...')
    optimizer_result = optimizer.optimize(constraints_object, discretized_tas)

    logger.debug('Optimizing on Upper Bound Constraints Object...')
    integer_program = IntegerProgram()
    upper_bound_optimizer_result = integer_program.compute_upper_bound_optimization(ub_constraints_object, discretized_tas)

    logger.debug('Scheduling...')
    schedules = scheduler.schedule(constraints_object, optimizer_result)

    # for schedule in schedules:
    #     logger.debug(schedule.channel.frequency.value)
    #     txops = []
    #     for txop in schedule.txops:
    #         txops.append(txop)
    #     txops.sort(key=lambda x: x.start_usec)
    #     for txop in txops:
    #          print(txop.start_usec, txop.stop_usec)

    logger.debug('Computing maximum channel efficiency...')
    channel_efficiency = scheduler.compute_max_channel_efficiency(constraints_object, optimizer_result)

    logger.debug('Exporting raw results...')
    file = determine_file_name(discretizer, optimizer, scheduler, timestamp, perturb_optimizer_result)
    csv_output = RAW_DIR + '/' + file + '.csv'
    export_raw(csv_output, optimizer, discretizer, optimizer_result, upper_bound_optimizer_result, channel_efficiency, constraints_object)

    if config.orientdb == 1:
        logger.debug('Generating new MDL files...')
        update_mdl_schedule(schedules)

        logger.debug('Exporting MDL file...')
        mdl_output = MDL_DIR + '/' + file + '.xml'
        export_mdl(mdl_output)

    if config.visualize == 1:
        os.system("start /wait cmd /c \
                   python \
                   {0}/external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py \
                   {1}".format(CP1_PARENT_FOLDER, mdl_output))

    return optimizer_result


logger.debug(STARTING_MESSAGE)
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
config = ConfigurationObject(CONFIG_FILE)

if config.clear == 1:
    logger.debug('Deleting previous runs...')
    clear_files([RAW_DIR, MDL_DIR])

if config.orientdb == 1:
    logger.debug('Generating shell MDL File...')
    generate_mdl_shell(
        ta_count=config.num_tas,
        output=MDL_SHELL_FILE,
        base=BASE_MDL_SHELL_FILE)

    logger.debug('Importing shell MDL File...')
    import_shell_mdl_file()

logger.debug('Generating Constraints Objects...')
constraints_object_list = ConstraintsObjectGenerator.generate(config)

logger.debug('Setting up Perturbation Object...')
perturber = Perturber(config)

logger.debug('Storing and Retrieving Constraints in OrientDB...')
if config.orientdb == 1:
    constraints_object_list = store_and_retrieve_constraints(constraints_object_list)
    logger.debug(constraints_object_list)

logger.debug('Setting up Discretizers...')
discretizers = setup_discretizers(config)

logger.debug('Setting up Optimizers...')
optimizers = setup_optimizers(config)

logger.debug('Setting up Schedulers...')
schedulers = setup_schedulers(config)

for constraints_object in constraints_object_list:
    for discretizer in discretizers:
        for optimizer in optimizers:
            for scheduler in schedulers:
                optimizer_result = solve_challenge_problem_instance(constraints_object, discretizer, optimizer, scheduler)

                # If nothing has been scheduled, there is nothing to perturb
                if config.perturb == 1:
                    if len(optimizer_result.scheduled_tas_list) != 0:
                        solve_challenge_problem_instance(constraints_object, discretizer, optimizer, scheduler, perturb_optimizer_result=optimizer_result)

                logger.debug(instance_completion_message(discretizer, optimizer, scheduler))

logger.debug(ENDING_MESSAGE)
