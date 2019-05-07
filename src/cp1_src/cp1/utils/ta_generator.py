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

logger = Logger().logger


class TAGenerator(DataGenerator):
    def __init__(
            self,
            lower_minimum_voice_bandwidth=Kbps(50),
            upper_minimum_voice_bandwidth=Kbps(200),
            lower_minimum_safety_bandwidth=Kbps(100),
            upper_minimum_safety_bandwidth=Kbps(8000),
            lower_latency=Milliseconds(50),
            upper_latency=Milliseconds(100),
            lower_scaling_factor=0.5,
            upper_scaling_factor=3,
            lower_c=0.0005,
            upper_c=0.007,
            seed=time.time()):
        self.lower_minimum_voice_bandwidth = lower_minimum_voice_bandwidth
        self.upper_minimum_voice_bandwidth = upper_minimum_voice_bandwidth
        self.lower_minimum_safety_bandwidth = lower_minimum_safety_bandwidth
        self.upper_minimum_safety_bandwidth = upper_minimum_safety_bandwidth
        self.lower_latency = lower_latency
        self.upper_latency = upper_latency
        self.lower_scaling_factor = float(lower_scaling_factor)
        self.upper_scaling_factor = float(upper_scaling_factor)
        self.lower_c = float(lower_c)
        self.upper_c = float(upper_c)

        random.seed(seed)
        numpy.random.seed(seed)

        self._validate()

    def generate(self, num_tas):
        """
        Generates a set amount of TAs in the range of data provided by data_generator.json.
        :param int num_tas: Number of TAs to generate
        """
        data_file = open('../../../conf/data_generator.json')
        data = json.load(data_file)
        voice_percentages = data['TA Generator']['voice_bandwidth']['percentages']
        voice_ranges = data['TA Generator']['voice_bandwidth']['ranges']
        safety_percentages = data['TA Generator']['safety_bandwidth']['percentages']
        safety_ranges = data['TA Generator']['safety_bandwidth']['ranges']
        latency_percentages = data['TA Generator']['latency']['percentages']
        latency_ranges = data['TA Generator']['latency']['ranges']
        scaling_percentages = data['TA Generator']['scaling_factor']['percentages']
        scaling_ranges = data['TA Generator']['scaling_factor']['ranges']
        c_percentages = data['TA Generator']['c']['percentages']
        c_ranges = data['TA Generator']['c']['ranges']
        data_file.close()

        tas = []
        for x in range(num_tas):
            tas.append(TA(
                id_='TA{0}'.format(x+1),
                minimum_voice_bandwidth=Kbps(
                    choice(self._generate_within_ranges(voice_ranges), p=voice_percentages)),
                minimum_safety_bandwidth=Kbps(
                    choice(self._generate_within_ranges(safety_ranges), p=safety_percentages)),
                latency=Milliseconds(choice(self._generate_within_ranges(
                    latency_ranges), p=latency_percentages)),
                scaling_factor=choice(self._generate_within_ranges(
                    scaling_ranges), p=scaling_percentages),
                c=choice(self._generate_within_ranges(
                    c_ranges), p=c_percentages),
                # Stub out eligible frequencies for now.
                eligible_channels=[Frequency(1000)]))
        return tas

    def generate_uniformly(self, num_tas):
        """
        Generates data within the bounds provided with equal probability.
        :param int num_tas: Number of TAs to generate
        """
        tas = []
        for x in range(num_tas):
            tas.append(
                TA(
                    id_='TA{0}'.format(x+1),
                    minimum_voice_bandwidth=Kbps(random.randint(
                        self.lower_minimum_voice_bandwidth.value,
                        self.upper_minimum_voice_bandwidth.value)),
                    minimum_safety_bandwidth=Kbps(random.randint(
                        self.lower_minimum_safety_bandwidth.value,
                        self.upper_minimum_safety_bandwidth.value)),
                    latency=Milliseconds(random.randint(
                        self.lower_latency.value, self.upper_latency.value)),
                    scaling_factor=random.uniform(
                        self.lower_scaling_factor, self.upper_scaling_factor),
                    c=random.uniform(self.lower_c, self.upper_c),
                    # Stub out eligible frequencies for now.
                    eligible_channels=[Frequency(1000)]))
        return tas

    def _validate(self):
        if self.upper_minimum_voice_bandwidth.value > 300:
            logger.warning('upper_minimum_voice_bandwidth ({0}) should be less than 300'.format(
                self.upper_minimum_voice_bandwidth.value))
        if self.upper_minimum_safety_bandwidth.value > 100:
            logger.warning('upper_minimum_safety_bandwidth ({0}) should be less than 100'.format(
                self.upper_minimum_safety_bandwidth.value))
        if self.upper_minimum_safety_bandwidth.value > 8000:
            logger.warning('TAGenerator.validate_ranges: upper_minimum_safety_bandwidth ({0}) must be less than 8000'.format(
                self.upper_minimum_safety_bandwidth.value))
        if self.upper_c > 1:
            logger.warning(
                'TAGenerator.validate_ranges: upper_c ({0}) must be less than 1'.format(self.upper_c))
        if self.upper_scaling_factor > 10:
            logger.warning('TAGenerator.validate_ranges: upper_scaling_factor ({0}) must be less than 10'.format(
                self.upper_scaling_factor))
        if self.lower_scaling_factor < 0:
            raise TAGeneratorRangeException(
                'lower_scaling_factor ({0}) must be greater than 0'.format(
                    self.lower_scaling_factor),
                'TAGenerator.validate_ranges')
        if self.lower_c < 0:
            raise TAGeneratorRangeException(
                'lower_c ({0}) must be greater than 0'.format(self.lower_c),
                'TAGenerator.validate_ranges')
        if self.lower_scaling_factor > self.upper_scaling_factor:
            raise TAGeneratorRangeException(
                'lower_scaling_factor ({0}) must be less than or equal to upper_scaling_factor ({1})'.format(
                    self.lower_scaling_factor,
                    self.upper_scaling_factor),
                'TAGenerator.validate_ranges')
        if self.lower_latency.value > self.upper_latency.value:
            raise TAGeneratorRangeException(
                'lower_latency ({0}) must be less than or equal to upper_latency ({1})'.format(
                    self.lower_latency.value,
                    self.upper_latency.value),
                'TAGenerator.validate_ranges')
        if self.lower_c > self.upper_c:
            raise TAGeneratorRangeException(
                'lower_c ({0}) must be less than or equal to upper_c ({1})'.format(
                    self.lower_c, self.upper_c),
                'TAGenerator.validate_ranges')
