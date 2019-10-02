from cp1.algorithms.optimizers.integer_program import IntegerProgram
from cp1.algorithms.optimizers.greedy_optimizer import GreedyOptimizer
from cp1.algorithms.schedulers.conservative_scheduler import ConservativeScheduler
from cp1.algorithms.schedulers.hybrid_scheduler import HybridScheduler
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
from collections import defaultdict
from cp1.common.exception_class import InvalidLatencyRequirementException

logger = Logger()
logger.setup_file_handler(os.path.abspath(LOGGING_DIR))
logger = logger.logger
timestamp = None

total_runs = 0
averages = {}
averages['Minimum Bandwidth'] = [0, 0, 0]
averages['Channel Dropoff'] = [0, 0, 0]
averages['Channel Capacity'] = [0, 0, 0]
averages['Perturbations'] = [0, 0, 0]
averages['Lower Bound'] = 0
averages['Optimized'] = 0
averages['Upper Bound'] = 0

def solve_challenge_problem_instance(
        constraints_object,
        discretizer,
        optimizer,
        scheduler,
        config,
        perturber=None,
        optimizer_result=None,
        webserver=False):
    """Runs through all steps required to solve a challenge problem instance.

    :param ConstraintsObject constraints_object: A Constraints Object containing all data necessary to optimize over.
    :param Discretizer discretizer: The discretizer algorithm to use when discretizing TAs
    :param Optimizer optimizer: The optimizer algorithm to use when optimizing TAs
    :param Scheduler scheduler: The scheduler algorithm to use when scheduling TAs
    :param Perturber perturber: The perturber to use when perturbing this solution
    :param OptimizerResult optimizer_result: The optimizer result to perturb
    :param Boolean visualize: Returns an array of visualization points if set to true
    :returns OptimizationResult:
    """
    global timestamps
    unadapted_value = ''
    if perturber is not None:
        logger.debug('Perturbing...')
        (constraints_object, unadapted_value) = perturber.perturb_constraints_object(
            constraints_object, optimizer_result)

    logger.debug('Discretizing...')
    discretized_tas = discretizer.discretize(constraints_object)

    logger.debug('Optimizing...')
    optimizer_result = optimizer.optimize(
        constraints_object,
        discretized_tas,
        discretizer.disc_count)

    logger.debug('Scheduling...')
    try:
        schedules = scheduler.schedule(constraints_object, optimizer_result)
    except InvalidLatencyRequirementException:
        schedules = ConservativeScheduler().schedule(constraints_object, optimizer_result)

    # Update the average values
    logger.debug('Computing lower and upper solution bounds...')
    integer_program = IntegerProgram()
    upper_bound_value = integer_program.compute_upper_bound_optimization(
        deepcopy(constraints_object), deepcopy(discretized_tas), discretizer.disc_count).value
    greedy_optimizer = GreedyOptimizer()
    lower_bound_value = greedy_optimizer.optimize(deepcopy(constraints_object), deepcopy(discretized_tas), discretizer.disc_count).value

    if perturber is not None:
        perturbation_bandwidth = sum(ta.bandwidth.value for ta in optimizer_result.scheduled_tas)
        # logger.debug('{0}_{1}_{2}_{3}_{4}'.format(str(perturber), optimizer_result.value, perturbation_bandwidth, unperturbed_value, original_total_bandwidth))
        # logger.debug('Post perturbation TAs')
        # for ta in optimizer_result.scheduled_tas:
        #     logger.debug('{0}'.format(ta.id_))
        # logger.debug('Original TAs')
        # for ta in original_tas:
        #     logger.debug('{0}'.format(ta.id_))
        if perturber.combine == 1:
                averages['Perturbations'][1] = optimizer_result.value
                averages['Perturbations'][2] = unadapted_value
        else:
            if perturber.ta_bandwidth != 0:
                averages['Minimum Bandwidth'][1] += optimizer_result.value
                averages['Minimum Bandwidth'][2] += unadapted_value
            elif perturber.channel_dropoff > 0:
                averages['Channel Dropoff'][1] += optimizer_result.value
                averages['Channel Dropoff'][2] += unadapted_value
            elif perturber.channel_capacity != 0:
                averages['Channel Capacity'][1] += optimizer_result.value
                averages['Channel Capacity'][2] += unadapted_value
    else:
        global total_runs
        total_runs += 1
        averages['Lower Bound'] += lower_bound_value
        averages['Optimized'] += optimizer_result.value
        averages['Upper Bound'] += upper_bound_value

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
        upper_bound_value,
        lower_bound_value,
        unadapted_value,
        channel_efficiency,
        constraints_object.seed)

    logger.debug('Exporting visual results...')
    visual_csv_file_name = str(constraints_object.seed) + '_' + csv_file_name
    visual_csv_output = VISUAL_DIR + '/' + visual_csv_file_name + '.csv'
    export_visual(visual_csv_output, optimizer_result)

    if config.orientdb == 1:
        logger.debug('Updating MDL file in OrientDB...')
        update_mdl_schedule(schedules)

        logger.debug('Exporting MDL file as xml...')
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
        logger.debug('Visualizing MDL file...')
        os.system("start /wait cmd /c \
                   python \
                   {0}/external/TxOpScheduleViewer/brass_visualization_tools/TxOpSchedViewer.py \
                   {1}".format(CP1_FOLDER, mdl_output))

    if webserver:
        return visualization_points
    else:
        return optimizer_result


def start(config=None, **kwargs):
    """Starts the CP1 framework

    :param ConfigurationObject config: A configurations object with the
                                                     parameters necessary to run CP1
    """
    logger.debug(STARTING_MESSAGE)

    global timestamp
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
                    optimizer_result = solve_challenge_problem_instance(
                        co, discretizer, optimizer, scheduler, config)

                    unperturbed_value = optimizer_result.value
                    # original_tas = optimizer_result.scheduled_tas
                    # original_total_bandwidth = sum(ta.bandwidth.value for ta in original_tas)
                    if config.combine == 1:
                        averages['Perturbations'][0] += unperturbed_value
                    else:
                        averages['Minimum Bandwidth'][0] += unperturbed_value
                        averages['Channel Dropoff'][0] += unperturbed_value
                        averages['Channel Capacity'][0] += unperturbed_value

                    for perturber in perturbers:
                        co_ = deepcopy(co)
                        or_ = deepcopy(optimizer_result)
                        # If nothing has been scheduled, there is nothing to perturb
                        if len(optimizer_result.scheduled_tas) != 0:
                            logger.debug(perturb_message(perturber))
                            solve_challenge_problem_instance(
                                co_, discretizer, optimizer, scheduler, config,
                                perturber, or_)

    for average_type, average_value in averages.items():
        if isinstance(average_value, list):
            averages[average_type] = list(map(lambda x: x / total_runs, average_value))
        else:
            averages[average_type] = average_value / total_runs

    logger.debug(ending_message(total_runs, averages, config.combine))

start()
