"""ta_generator.py

Constructs a set of TA equations based on the provided input.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import json
import random
import os
import numpy
import time
from datetime import timedelta

from cp1.utils.data_generator import DataGenerator
from cp1.utils.json_utils import extract_percentages
from cp1.data_objects.mdl.frequency import Frequency
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

    def generate(self, channels, seed=None):
        """
        Generates a set amount of TAs in the range of data provided by data_file
        :param str data_file_path: Path to file containing generation values
        :param int seed: The number to seed random and numpy.random with
        """
        self._extract_data()
        self._validate(channels)

        if seed is not None:
            random.seed(seed)
            numpy.random.seed(seed)

        tas = []
        for x in range(self.num_tas):
            eligible_channels = []
            num_eligible_channels = numpy.random.choice(self._generate_within_ranges(
                                            self.eligible_channels), p=extract_percentages(self.eligible_channels))
            for i in range(num_eligible_channels):
                eligible_channels.append(channels[i])

            tas.append(TA(
                id_='TA{0}'.format(x + 1),
                minimum_voice_bandwidth=Kbps(
                    numpy.random.choice(self._generate_within_ranges(self.voice, seed), p=extract_percentages(self.voice))),
                minimum_safety_bandwidth=Kbps(
                    numpy.random.choice(self._generate_within_ranges(self.safety, seed), p=extract_percentages(self.safety))),
                latency=timedelta(microseconds=1000*int(numpy.random.choice(self._generate_within_ranges(
                    self.latency, seed), p=extract_percentages(self.latency)))),
                scaling_factor=numpy.random.choice(self._generate_within_ranges(
                    self.scaling, seed), p=extract_percentages(self.scaling)),
                c=numpy.random.choice(self._generate_within_ranges(
                    self.c, seed), p=extract_percentages(self.c)),
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
                self.eligible_channels = data['TAs']['eligible_channels']
                self.voice = data['TAs']['voice_bandwidth']
                self.safety = data['TAs']['safety_bandwidth']
                self.latency = data['TAs']['latency']
                self.scaling = data['TAs']['scaling_factor']
                self.c = data['TAs']['c']
                self.eligible_channels = data['TAs']['eligible_channels']
                self.base_frequency = data['Channels']['base_frequency']
            except Exception as ex:
                raise ConfigFileException(ex, 'TAGenerator._extract_data')

    def _validate(self, channels):
        self._validate_eligible_channels(self.eligible_channels, channels)
        self.validate_num_to_generate('num_tas', self.num_tas)
        self.validate_distribution_schema('eligible_channels', self.eligible_channels)
        self.validate_distribution_schema('voice_bandwidth', self.voice)
        self.validate_distribution_schema('safety_bandwidth', self.safety)
        self.validate_distribution_schema('latency', self.latency)
        self.validate_distribution_schema('scaling_factor', self.scaling)
        self.validate_distribution_schema('c', self.c)

    def _validate_eligible_channels(self, eligible_channels, all_channels):
        for eligible_channel in eligible_channels:
            eligible_channel_list = eligible_channel[1]
            for num in eligible_channel_list:
                if num > len(all_channels):
                    raise ConfigFileException('There cannot be more eligible_channels ({0}) than total channels ({1})'.format(num, len(all_channels)))
