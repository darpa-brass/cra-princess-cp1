"""ta_generator.py

Constructs a set of TA equations based on the provided input.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import random
from numpy.random import choice
from cp1.data_objects.processing.ta import TA
from cp1.data_objects.mdl.mdl_id import MdlId
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.mdl.frequency import Frequency
from cp1.common.exception_class import TAGeneratorRangeException
from cp1.utils.data_generator import DataGenerator
from cp1.common.logger import Logger
import json

logger = Logger().logger

class TAGenerator(DataGenerator):
    def __init__(
            self,
            lower_minimum_voice_bandwidth=Kbps(50),
            upper_minimum_voice_bandwidth=Kbps(200),
            lower_minimum_safety_bandwidth=Kbps(100),
            upper_minimum_safety_bandwidth=Kbps(8000),
            lower_scaling_factor=0.5,
            upper_scaling_factor=3,
            lower_c=0.0005,
            upper_c=0.007):
        self.lower_minimum_voice_bandwidth = lower_minimum_voice_bandwidth
        self.upper_minimum_voice_bandwidth = upper_minimum_voice_bandwidth
        self.lower_minimum_safety_bandwidth = lower_minimum_safety_bandwidth
        self.upper_minimum_safety_bandwidth = upper_minimum_safety_bandwidth
        self.lower_scaling_factor = float(lower_scaling_factor)
        self.upper_scaling_factor = float(upper_scaling_factor)
        self.lower_c = float(lower_c)
        self.upper_c = float(upper_c)

        self._validate()

    def generate(self, num_tas):
        data_file = open('../../../../conf/data_generator.json', 'r')
        data = json.load(data_file)
        scaling_percentages = data['TA Generator']['scaling_factor']['percentages']
        scaling_ranges = data['TA Generator']['scaling_factor']['ranges']
        voice_percentages = data['TA Generator']['voice_bandwidth']['percentages']
        voice_ranges = data['TA Generator']['voice_bandwidth']['ranges']
        safety_percentages = data['TA Generator']['safety_bandwidth']['percentages']
        safety_ranges = data['TA Generator']['safety_bandwidth']['ranges']
        c_percentages = data['TA Generator']['c']['percentages']
        c_ranges = data['TA Generator']['c']['ranges']
        data_file.close()

        tas = []
        for i in range(0, num_tas):
            tas.append(TA(
                id_=MdlId('TA{0}'.format(i+1)),
                minimum_voice_bandwidth=Kbps(choice(self._generate_within_ranges(voice_ranges), p=voice_percentages)),
                minimum_safety_bandwidth=Kbps(choice(self._generate_within_ranges(safety_ranges), p=safety_percentages)),
                scaling_factor=choice(self._generate_within_ranges(scaling_ranges), p=scaling_percentages),
                c=choice(self._generate_within_ranges(c_ranges), p=c_percentages)))
        return tas

    def generate_uniformly(self, num_tas):
        random.seed(1)
        MdlId.clear()
        ta_equations = []
        for x in range(num_tas):
            voice = random.randint(
                self.lower_minimum_voice_bandwidth.value,
                self.upper_minimum_voice_bandwidth.value)
            safety = random.randint(
                self.lower_minimum_safety_bandwidth.value,
                self.upper_minimum_safety_bandwidth.value)
            scaling_factor = random.uniform(
                self.lower_scaling_factor, self.upper_scaling_factor)
            c = random.uniform(self.lower_c, self.upper_c)

            ta_equations.append(
                TA(
                    id_=MdlId('TA{0}'.format(x+1)),
                    minimum_voice_bandwidth=Kbps(voice),
                    minimum_safety_bandwidth=Kbps(safety),
                    scaling_factor=scaling_factor,
                    c=c))

        return ta_equations

    def _validate(self):
        if self.upper_minimum_voice_bandwidth.value > 200:
            logger.warning('TAGenerator.validate_ranges: upper_minimum_voice_bandwidth must be less than 200: {0}'.format(
                    self.upper_minimum_voice_bandwidth.value))
        if self.upper_minimum_safety_bandwidth.value > 8000:
            logger.warning('TAGenerator.validate_ranges: upper_minimum_safety_bandwidth must be less than 8000: {0}'.format(
                    self.upper_minimum_safety_bandwidth.value))
        if self.upper_c > 1:
            logger.warning('TAGenerator.validate_ranges: upper_c must be less than 1'.format(self.upper_c))
        if self.upper_scaling_factor > 10:
            logger.warning('TAGenerator.validate_ranges: upper_scaling_factor must be less than 10'.format(
                    self.upper_scaling_factor))
        if self.lower_scaling_factor < 0:
            raise TAGeneratorRangeException(
                'lower_scaling_factor must be greater than 0'.format(
                    self.lower_scaling_factor),
                'TAGenerator.validate_ranges')
        if self.lower_c < 0:
            raise TAGeneratorRangeException(
                'lower_c must be greater than 0'.format(self.lower_c),
                'TAGenerator.validate_ranges')
        if self.lower_scaling_factor > self.upper_scaling_factor:
            raise TAGeneratorRangeException(
                'lower_scaling_factor: {0} must be less than or equal to upper_scaling_factor: {1}'.format(
                    self.lower_scaling_factor,
                    self.upper_scaling_factor),
                'TAGenerator.validate_ranges')
        if self.lower_c > self.upper_c:
            raise TAGeneratorRangeException(
                'lower_c: {0} must be less than or equal to upper_c: {1}'.format(
                    self.lower_c, self.upper_c),
                'TAGenerator.validate_ranges')
