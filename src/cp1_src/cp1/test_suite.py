import os
from cp1.common.logger import Logger
logger = Logger()
logger.setup_file_handler(os.path.abspath('../../../logs/'))
logger = logger.logger

from ortools.linear_solver import pywraplp
from copy import deepcopy
from datetime import timedelta
import time
import csv
import json
import sys
import re
import shutil
import subprocess

from brass_mdl_tools.mdl_generator import generate_mdl_shell
from cp1.data_objects.processing.channel import Channel
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.bandwidth_types import BandwidthTypes
from cp1.data_objects.mdl.bandwidth_rate import BandwidthRate
from cp1.data_objects.mdl.txop_timeout import TxOpTimeout
from cp1.data_objects.mdl.txop import TxOp
from cp1.data_objects.mdl.frequency import Frequency
from cp1.utils.data_generators.ta_generator import TAGenerator
from cp1.utils.data_generators.channel_generator import ChannelGenerator
from cp1.utils.decorators.orientdb_exporter import OrientDBExporter
from cp1.utils.decorators.orientdb_importer import OrientDBImporter
from cp1.utils.orientdb.orientdb_session import OrientDBSession
from cp1.processing.algorithms.scheduling.greedy_schedule import GreedySchedule
from cp1.processing.algorithms.optimization.greedy_optimization import GreedyOptimization
from cp1.processing.algorithms.optimization.dynamic_program import DynamicProgram
from cp1.processing.algorithms.optimization.integer_program import IntegerProgram
from cp1.processing.algorithms.discretization.value_discretization import ValueDiscretization
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization


def baseline_data_generation():
    channel = Channel()
    ta1 = TA(id_='TA1', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=time_(microsecond=50000), scaling_factor=1, c=0.005, channel=channel)
    ta2 = TA(id_='TA2', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=time_(microsecond=50000), scaling_factor=1, c=0.005, channel=channel)
    ta3 = TA(id_='TA3', bandwidth=Kbps(2000), minimum_voice_bandwidth=Kbps(1500), minimum_safety_bandwidth=Kbps(1500), latency=time_(microsecond=20000), scaling_factor=1, c=0.005, channel=channel)
    candidate_tas = [ta1, ta2, ta3]

    constraints_object = ConstraintsObject(id_='C1', candidate_tas=candidate_tas, channels=[channel], epoch=time_(microsecond=100000))
    algorithm_result = AlgorithmResult(constraints_object = constraints_object, scheduled_tas=candidate_tas, run_time=0.5, solve_time=0.5, value=1000)

    hybrid_scheduler = HybridScheduler()
    new_schedule = hybrid_scheduler.schedule(algorithm_result=algorithm_result)
