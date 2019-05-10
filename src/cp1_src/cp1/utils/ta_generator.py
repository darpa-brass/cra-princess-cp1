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
from cp1.utils.data_generator import DataGenerator
from cp1.data_objects.mdl.frequency import Frequency
from cp1.common.logger import Logger
from cp1.common.exception_class import TAGeneratorRangeException
from cp1.data_objects.mdl.milliseconds import Milliseconds
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.channel import Channel
from cp1.utils.json_utils import extract_percentages
from cp1.common.exception_class import ConfigFileException

logger = Logger().logger


class TAGenerator(DataGenerator):
    def __init__(self):
        self._extract_data()
        self._validate()

    def generate(self):
        """
        Generates a set amount of TAs in the range of data provided by data_generator.json.
        :param int num_tas: Number of TAs to generate
        """
        tas = []
        for x in range(self.num_tas):
            tas.append(TA(
                id_='TA{0}'.format(x+1),
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
                # Stub out eligible frequencies for now.
                eligible_channels=[Frequency(1000)]))
        return tas

    def _extract_data(self):
        data_file = open('C:/dev/cp1/conf/data.json')
        data = json.load(data_file)
        try:
            self.num_tas = data['TAs']['num_tas']
            self.seeds = data['TAs']['seeds']
            self.channels = data['TAs']['eligible_channels']
            self.voice = data['TAs']['voice_bandwidth']
            self.safety = data['TAs']['safety_bandwidth']
            self.latency = data['TAs']['latency']
            self.scaling = data['TAs']['scaling_factor']
            self.c = data['TAs']['c']
        except Exception as ex:
            raise ConfigFileException(ex, 'TAGenerator._extract_data')
        data_file.close()


    def _validate(self):
        self.validate_seeds(self.seeds)
        self.validate_num_to_generate('num_tas', self.num_tas)
        self.validate_distribution_schema('eligible_channels', self.channels)
        self.validate_distribution_schema('voice_bandwidth', self.voice)
        self.validate_distribution_schema('safety_bandwidth', self.safety)
        self.validate_distribution_schema('latency', self.latency)
        self.validate_distribution_schema('scaling_factor', self.scaling)
        self.validate_distribution_schema('c', self.c)
