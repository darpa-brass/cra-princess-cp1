"""constants.py

A list of upper bounds and other constant values.
"""

from cp1.data_objects.mdl.kbps import Kbps
from datetime import timedelta


MAX_BANDWIDTH = Kbps(8000) # Maximum allowable bandwidth for any TA
DEADLINE_WINDOW = timedelta(microseconds=1000) # Amount to move a TA back by if there is a conflict in two TA's start deadline
GUARDBAND_OFFSET = timedelta(microseconds=1) # The difference in time between two TAs communicating should be the guard band + 1 microsecond.
DYNAMIC_PROGRAM_FACTOR = 3
ORIENTDB_CONSTRAINTS_TYPE = "System Wide Constraints"
