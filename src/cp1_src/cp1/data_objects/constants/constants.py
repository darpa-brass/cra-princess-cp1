'''constants.py

A list of upper bounds and other constant values.
Paths are relative to start.py.
'''

from cp1.data_objects.mdl.kbps import Kbps
from cp1.utils.decorators.timedelta import timedelta
from ortools.linear_solver import pywraplp

# MDL Constraints
MAX_BANDWIDTH = Kbps(8000) # Maximum allowable bandwidth for any TA
MDL_MIN_INTERVAL = timedelta(microseconds=500) # The minimum time interval allowed to be scheduled in an MDL file

# Optimization Parameters
DYNAMIC_PROGRAM_TABLE_QUANTIZATION = 2 # The number of minimum schedulable time units per millisecond
INTEGER_PROGRAM_TIME_LIMIT = 15 # OR Tools Solver engine time limit in seconds
INTEGER_PROGRAM_ENGINE = pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING

# OrientDB
ORIENTDB_CONFIG_FILE = '../../../conf/orientdb_config.json'
CONSTRAINTS_DB = 'cra_constraints'
MDL_DB = 'cra_mdl'

# Outputs and file generation relative to start.py
CONFIG_FILE = '../../../conf/config.json'
BASE_MDL_SHELL_FILE = '../../../external/TxOpScheduleViewer/brass_mdl_tools/base.xml'
MDL_SHELL_FILE = '../../../output/mdl/mdl_shell.xml'
MDL_DIR = '/data/mdl'
VISUAL_DIR = '/data/visual'
RAW_DIR = '/data/raw'
LOGGING_DIR = '/data/logs/'

# Paths
CP1_FOLDER = 'd:/dev/cp1' # Path to CP1

# The set of Mac abbreviations provided by SwRI used in MDL file RadioLink elements
GROUND_MAC = 0x1000
TA_MAC = 0x2000
UPLINK_MAC = 0xF000
DOWNLINK_MAC = 0xF100
