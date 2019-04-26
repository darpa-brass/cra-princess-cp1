"""bandwidth_types.py

Enum representing all possible bandwidth types.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from enum import Enum


class BandwidthTypes(Enum):
    VOICE = 1
    SAFETY = 2
    RFNM = 3
    BULK = 4
