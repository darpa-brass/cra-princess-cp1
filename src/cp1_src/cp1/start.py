from cp1.algorithms.optimizers.integer_program import IntegerProgram
from cp1.data_objects.processing.configuration_object import ConfigurationObject
from cp1.utils.constraints_object_generator import *
from cp1.utils.configuration_utils import *
from cp1.utils.string_utils import *
from cp1.utils.file_utils import *
from brass_mdl_tools.mdl_generator import generate_mdl_shell
from cp1.utils.decorators.timedelta import timedelta
from copy import deepcopy
import time
import os
from cp1.common.logger import Logger
from cp1.data_objects.constants.constants import *

logger = Logger()
logger.setup_file_handler(os.path.abspath(LOGGING_DIR))
logger = logger.logger


def solve_challenge_problem_instance(
        constraints_object,
        discretizer,
        optimizer,
        scheduler,
        perturber=None,
        optimizer_result=None):
    """Runs through all steps required to solve a challenge problem instance.

    :param ConstraintsObject constraints_object: A Constraints Object containing all data necessary to optimize over.
    :param Discretizer discretizer: The discretizer algorithm to use when discretizing TAs
    :param Optimizer optimizer: The optimizer algorithm to use when optimizing TAs
    :param Scheduler scheduler: The scheduler algorithm to use when scheduling TAs
    :param Perturber perturber: The perturber to use when perturbing this solution
    :param OptimizerResult optimizer_result: The optimizer result to perturb
    :returns OptimizationResult:
    """
    ub_constraints_object = deepcopy(constraints_object)

    if perturber is not None:
        logger.debug('Perturbing Constraints Object...')
        constraints_object = perturber.perturb_constraints_object(
            constraints_object, optimizer_result)

    discretized_tas = discretizer.discretize(constraints_object)
    ub_discretized_tas = deepcopy(discretized_tas)

    logger.debug('Optimizing Constraints Object...')
    optimizer_result = optimizer.optimize(
        constraints_object,
        discretized_tas,
        discretizer.disc_count)

    if perturber is not None:
        logger.debug('Scheduled TAs after Perturbation')
    else:
        logger.debug('Scheduled TAs before Perturbation')
    for ta in optimizer_result.scheduled_tas:
        logger.debug('{0}_{1}_{2}'.format(ta.id_, ta.latency, ta.bandwidth.value))

    logger.debug('Optimizing on Upper Bound Constraints Object...')
    integer_program = IntegerProgram()
    upper_bound_optimizer_result = integer_program.compute_upper_bound_optimization(
        ub_constraints_object, ub_discretized_tas, discretizer.disc_count)

    # for channel in constraints_object.channels:
    #     print(channel)
    # logger.debug('Printing out Upper Bound TAs:')
    # for ta in upper_bound_optimizer_result.scheduled_tas:
    #     print(ta.id_, ta.value, ta.bandwidth.value, ta.latency.get_microseconds(), ta.compute_communication_length(ta.channel.capacity, ta.latency, ub_constraints_object.guard_band).get_microseconds(), ta.channel.frequency.value)
    # for channel in ub_constraints_object.channels:
    #     print(channel)

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
    channel_efficiency = scheduler.compute_max_channel_efficiency(
        optimizer_result)

    logger.debug('Exporting raw results...')
    csv_file_name = determine_file_name(
        discretizer,
        optimizer,
        scheduler,
        timestamp,
        perturber)
    csv_output = RAW_DIR + '/' + csv_file_name + '.csv'

    export_raw(
        csv_output,
        optimizer,
        discretizer,
        optimizer_result,
        # upper_bound_optimizer_result,
        channel_efficiency,
        constraints_object)

    visual_csv_file_name = 'Visual_' + \
        str(constraints_object.seed) + '_' + csv_file_name
    visual_csv_output = VISUAL_DIR + '/' + visual_csv_file_name + '.csv'
    export_visual(visual_csv_output, optimizer_result)

    if config.orientdb == 1:
        logger.debug('Generating new MDL files...')
        update_mdl_schedule(schedules)

        logger.debug('Exporting MDL file...')
        mdl_file_name = determine_file_name(
            discretizer,
            optimizer,
            scheduler,
            timestamp,
            perturber,
            constraints_object.seed)
        mdl_output = MDL_DIR + '/' + mdl_file_name + '.xml'
        export_mdl(mdl_output)

    if config.visualize == 1:
        os.system("start /wait cmd /c \
                   python \
                   {0}/external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py \
                   {1}".format(CP1_FOLDER, mdl_output))

    return optimizer_result


logger.debug(STARTING_MESSAGE)
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
config = ConfigurationObject(CONFIG_FILE)

if config.clear == 1:
    logger.debug('Deleting previous runs...')
    clear_files([RAW_DIR, MDL_DIR, VISUAL_DIR])

if config.orientdb == 1:
    logger.debug('Generating shell MDL File...')
    generate_mdl_shell(
        ta_count=config.num_tas,
        output=MDL_SHELL_FILE,
        base=BASE_MDL_SHELL_FILE,
        add_rans=config.num_channels - 1)

    logger.debug('Importing shell MDL File...')
    import_shell_mdl_file()

logger.debug('Generating Constraints Objects...')
constraints_object_list = ConstraintsObjectGenerator.generate(config)

logger.debug('Setting up Discretizers...')
discretizers = setup_discretizers(config)

logger.debug('Setting up Optimizers...')
optimizers = setup_optimizers(config)

logger.debug('Setting up Schedulers...')
schedulers = setup_schedulers(config)

logger.debug('Setting up Perturbers...')
perturbers = setup_perturbers(config)

for constraints_object in constraints_object_list:
    for discretizer in discretizers:
        for optimizer in optimizers:
            for scheduler in schedulers:
                logger.debug(
                    instance_message(
                        constraints_object.seed,
                        discretizer,
                        optimizer,
                        scheduler))

                optimizer_result = solve_challenge_problem_instance(
                    constraints_object, discretizer, optimizer, scheduler)

                for perturber in perturbers:

                    # If nothing has been scheduled, there is nothing to perturb
                    if len(optimizer_result.scheduled_tas) != 0:
                        logger.debug(perturb_message(perturber))

                        solve_challenge_problem_instance(
                            constraints_object, discretizer, optimizer, scheduler,
                            perturber, optimizer_result)

logger.debug(ENDING_MESSAGE)
