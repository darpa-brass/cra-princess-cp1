import time
import os
import shutil
from copy import deepcopy
from collections import defaultdict

from brass_mdl_tools.mdl_generator import generate_mdl_shell

from cp1.common.logger import Logger
from cp1.common.exception_class import InvalidLatencyRequirementException

from cp1.data_objects.processing.averages import Averages
from cp1.data_objects.constants.constants import *
from cp1.data_objects.processing.configuration_object import ConfigurationObject

from cp1.algorithms.optimizers.integer_program import IntegerProgram
from cp1.algorithms.optimizers.greedy_optimizer import GreedyOptimizer
from cp1.algorithms.schedulers.conservative_scheduler import ConservativeScheduler
from cp1.algorithms.schedulers.hybrid_scheduler import HybridScheduler

from cp1.utils.constraints_object_generator import *
from cp1.utils.configuration_utils import *
from cp1.utils.string_utils import *
from cp1.utils.file_utils import *
from cp1.utils.decorators.timedelta import timedelta

logger = Logger()
logger.setup_file_handler(os.path.abspath(LOGGING_DIR))
logger = logger.logger
timestamp = None
total_runs = 0

for dir in [RAW_DIR, LOGGING_DIR, MDL_DIR]:
    os.makedirs(dir, exist_ok=True)


def solve_challenge_problem_instance(
        constraints_object,
        discretizer,
        optimizer,
        scheduler,
        config,
        averages,
        perturber=None,
        optimizer_result=None,
        lower_bound_optimizer_result=None,
        webserver=False):
    """Runs through all steps required to solve a challenge problem instance.

    :param ConstraintsObject constraints_object: A Constraints Object containing all data necessary to optimize over.
    :param Discretizer discretizer: The discretizer algorithm to use when discretizing TAs
    :param Optimizer optimizer: The optimizer algorithm to use when optimizing TAs
    :param Scheduler scheduler: The scheduler algorithm to use when scheduling TAs
    :param Perturber perturber: The perturber to use when perturbing this solution
    :param OptimizerResult optimizer_result: The optimizer result to perturb
    :param OptimizerResult lower_bound_optimizer_result: The lower bound optimizer result to use when calculating averages
    :param Boolean visualize: Returns an array of visualization points if set to true
    :returns OptimizationResult:
    """
    global timestamps

    logger.debug('Discretizing...')
    discretized_tas = discretizer.discretize(constraints_object)

    logger.debug('Optimizing...')
    greedy_optimizer = GreedyOptimizer()
    lower_bound_or = greedy_optimizer.optimize(deepcopy(constraints_object), deepcopy(discretized_tas), discretizer.disc_count)
    logger.debug('Lower bound initial solution value (after selecting TAs): {0}'.format(lower_bound_or.value))

    logger.debug('Amount of TAs for regular: {0}'.format(len(discretized_tas)))
    cra_cp1_or = optimizer.optimize(
        deepcopy(constraints_object),
        deepcopy(discretized_tas),
        discretizer.disc_count)
    logger.debug('CRA CP1 initial solution value (after selecting TAs) is: {0}'.format(cra_cp1_or.value))

    integer_program = IntegerProgram()
    upper_bound_or = integer_program.compute_upper_bound_optimization(
        deepcopy(constraints_object), deepcopy(discretized_tas), discretizer.disc_count)
    logger.debug('Upper bound solution value (after selecting TAs) is: {0}'.format(upper_bound_or.value))

    logger.debug('Scheduling...')
    lower_bound_schedules = ConservativeScheduler().schedule(deepcopy(constraints_object), lower_bound_or)
    logger.debug('Channel efficiencies:')
    for schedule in lower_bound_schedules:
        efficiency = schedule.compute_bw_efficiency()
        logger.debug('{0}: {1}'.format(schedule.channel.frequency.value, efficiency))
    logger.debug('Lower Bound final solution value (after scheduling TAs) is: {0}'.format(sum([schedule.compute_bw_efficiency() for schedule in lower_bound_schedules])))

    try:
        cra_cp1_schedules = scheduler.schedule(constraints_object, cra_cp1_or)
    except InvalidLatencyRequirementException:
        logger.debug('CRA CP1: The latency of one or more TAs is too high to use the Hybrid Scheduler. Switching to Conservative Scheduler instead.')
        cra_cp1_schedules = ConservativeScheduler().schedule(constraints_object, cra_cp1_or)
    logger.debug('Channel efficiencies:')
    for schedule in cra_cp1_schedules:
        efficiency = schedule.compute_bw_efficiency()
        logger.debug('{0}: {1}'.format(schedule.channel.frequency.value, efficiency))
    logger.debug('CRA CP1 final solution value (after scheduling TAs) is: {0}'.format(sum([schedule.compute_bw_efficiency() for schedule in cra_cp1_schedules])))

    upper_bound_co = deepcopy(constraints_object)
    for ta in upper_bound_co.candidate_tas:
        ta.latency = upper_bound_co.epoch
    try:
        upper_bound_schedules = HybridScheduler().schedule(upper_bouund_co, upper_bound_or)
    except:
        logger.debug('Upper Bound: The latency of one or more TAs is too high to use the Hybrid Scheduler. Switching to Conservative Scheduler instead.')
        upper_bound_schedules = ConservativeScheduler().schedule(upper_bound_co, upper_bound_or)
    logger.debug('Channel efficiencies:')
    for schedule in upper_bound_schedules:
        efficiency = schedule.compute_bw_efficiency()
        logger.debug('{0}: {1}'.format(schedule.channel.frequency.value, efficiency))
    logger.debug('Upper Bound final solution value (after scheduling TAs) is: {0}'.format(sum([schedule.compute_bw_efficiency() for schedule in upper_bound_schedules])))

    logger.debug('Updating averages...')
    averages.update(perturber, lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules)

    logger.debug('Exporting raw results...')
    csv_file_name = determine_file_name(
        discretizer,
        optimizer,
        scheduler,
        total_runs,
        perturber)
    csv_output = RAW_DIR + '/' + csv_file_name + '.csv'

    export_raw(
        csv_output,
        optimizer,
        discretizer,
        lower_bound_or,
        cra_cp1_or,
        upper_bound_or,
        lower_bound_schedules,
        cra_cp1_schedules,
        upper_bound_schedules,
        constraints_object.seed)

    logger.debug('Exporting visual results...')
    visual_csv_file_name = str(constraints_object.seed) + '_' + csv_file_name
    visual_csv_output = VISUAL_DIR + '/' + visual_csv_file_name + '.csv'
    export_visual(visual_csv_output, cra_cp1_or)

    if config.orientdb == 1:
        logger.debug('Updating MDL file in OrientDB...')
        update_mdl_schedule(cra_cp1_schedules)

        logger.debug('Exporting MDL file as xml...')
        mdl_file_name = determine_file_name(
            discretizer,
            optimizer,
            scheduler,
            total_runs,
            perturber,
            constraints_object.seed)
        mdl_output = MDL_DIR + '/' + mdl_file_name + '.xml'
        export_mdl(mdl_output)

    if config.visualize == 1:
        logger.debug('Visualizing MDL file...')
        os.system("start /wait cmd /c \
                   python \
                   {0}/external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py \
                   {1}".format(CP1_FOLDER, mdl_output))

    if webserver:
        return visualization_points
    else:
        return (cra_cp1_or, lower_bound_or)


def start(config=None, **kwargs):
    """Starts the CP1 framework

    :param ConfigurationObject config: A configurations object with the
                                                     parameters necessary to run CP1
    """
    logger.debug(starting_message())

    global timestamp
    global total_runs
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    if config is None:
        config = ConfigurationObject(CONFIG_FILE, **kwargs)

    if config.clear == 1:
        logger.debug('Deleting previous runs...')
        clear_files([RAW_DIR, MDL_DIR, VISUAL_DIR])

    if config.orientdb == 1:
        logger.debug('Generating shell MDL File...')
        generate_mdl_shell(
            count=config.num_tas,
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

    logger.debug('Setting up Averages...')
    averages = Averages()
    for co in constraints_object_list:
        for discretizer in discretizers:
            for optimizer in optimizers:
                for scheduler in schedulers:
                    logger.debug(
                        instance_message(
                            co.id_,
                            co.seed,
                            discretizer,
                            optimizer,
                            scheduler))

                    (unperturbed_or, lower_bound_or) = solve_challenge_problem_instance(
                        co, discretizer, optimizer, scheduler, config, averages)
                    total_runs += 1

                    co_ = deepcopy(co)
                    or_ = deepcopy(unperturbed_or)
                    lower_bound_or = deepcopy(lower_bound_or)
                    # If nothing has been scheduled, there is nothing to perturb
                    if len(unperturbed_or.scheduled_tas) != 0:
                        for perturber in perturbers:
                            logger.debug(perturb_message(perturber))
                            (perturbed_co, unadapted_value) = perturber.perturb_constraints_object(
                                co_, unperturbed_or, lower_bound_or)
                            solve_challenge_problem_instance(perturbed_co, discretizer,
                                optimizer, scheduler, config, averages, perturber)


    averages.compute(total_runs)
    logger.debug(ending_message(total_runs, averages, config))

start()
