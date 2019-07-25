"""ta_generator.py

Constructs a set of TA equations based on the provided input.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import json
import random
import os
import numpy
import time
from numpy.random import choice

from cp1.utils.data_generators.data_generator import DataGenerator
from cp1.utils.file_utils.json_utils import extract_percentages
from cp1.data_objects.mdl.frequency import Frequency
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.channel import Channel
from cp1.common.logger import Logger
from cp1.common.exception_class import TAGeneratorRangeException
from cp1.common.exception_class import ConfigFileException

logger = Logger().logger


class TAGenerator(DataGenerator):
    def __init__(self, config_file):
        self.config_file = config_file

    def generate(self, channels):
        """
        Generates a set amount of TAs in the range of data provided by data_file
        :param str data_file_path: Path to file containing generation values
        """
        self._extract_data()
        self._validate()
        tas = []
        for x in range(self.num_tas):
            eligible_channels = []
            num_eligible_channels = choice(self._generate_within_ranges(
                                            self.eligible_channels), p=extract_percentages(self.eligible_channels))
            for i in range(num_eligible_channels):
                eligible_channels.append(channels[i])

            tas.append(TA(
                id_='TA{0}'.format(x + 1),
                minimum_voice_bandwidth=Kbps(
                    choice(self._generate_within_ranges(self.voice), p=extract_percentages(self.voice))),
                minimum_safety_bandwidth=Kbps(
                    choice(self._generate_within_ranges(self.safety), p=extract_percentages(self.safety))),
                latency=Milliseconds(choice(self._generate_within_ranges(
                    self.latency), p=extract_percentages(self.latency))),
                scaling_factor=choice(self._generate_within_ranges(
                    self.scaling), p=extract_percentages(self.scaling)),
                c=choice(self._generate_within_ranges(
                    self.c), p=extract_percentages(self.c)),
                eligible_channels = eligible_channels))
        return tas

    def _extract_data(self):
        """
        Attempts to open extract the values from data_file_path.
        """
        with open(self.config_file) as f:
            data = json.load(f)
            try:
                self.num_tas = data['TAs']['num_tas']
                self.channels = data['TAs']['eligible_channels']
                self.voice = data['TAs']['voice_bandwidth']
                self.safety = data['TAs']['safety_bandwidth']
                self.latency = data['TAs']['latency']
                self.scaling = data['TAs']['scaling_factor']
                self.c = data['TAs']['c']
                self.eligible_channels = data['TAs']['eligible_channels']
                self.base_frequency = data['Channels']['base_frequency']
            except Exception as ex:
                raise ConfigFileException(ex, 'TAGenerator._extract_data')

    def _validate(self):
        self.validate_num_to_generate('num_tas', self.num_tas)
        self.validate_distribution_schema('eligible_channels', self.channels)
        self.validate_distribution_schema('voice_bandwidth', self.voice)
        self.validate_distribution_schema('safety_bandwidth', self.safety)
        self.validate_distribution_schema('latency', self.latency)
        self.validate_distribution_schema('scaling_factor', self.scaling)
        self.validate_distribution_schema('c', self.c)
