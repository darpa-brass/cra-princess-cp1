"""data_generator.py

Interface for all data generators.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc
import random
from cp1.common.exception_class import ConfigFileException

class DataGenerator(abc.ABC):
    def _generate_within_ranges(self, ranges):
        """
        Takes in a field from data_generator.json and generates one value for each range.
        If either of the two numbers in the range are a float, it will produce a
        float.

        :param [[]] ranges: The list of ranges for a variable.

        :return [] vals: One value generated for each range.
        """
        vals = []
        for i in range(0, len(ranges)):
            if len(ranges[i][1]) == 1:
                vals.append(ranges[i][1][0])
            else:
                if isinstance(ranges[i][1][0], float) or isinstance(ranges[i][1][1], float):
                    vals.append(random.uniform(
                        ranges[i][1][0], ranges[i][1][1]))
                else:
                    vals.append(random.randint(
                        ranges[i][1][0], ranges[i][1][1]
                    ))
        return vals

    @abc.abstractmethod
    def _validate(self):
        pass

    @abc.abstractmethod
    def _extract_data(self):
        pass

    @abc.abstractmethod
    def generate(self, num):
        pass

    def validate_base_frequency(self, base_frequency):
        if not isinstance(base_frequency[0], int) or base_frequency[0] < 0:
            raise ConfigFileException(
                'Base Frequency ({0}) must be an int greater than 0'.format(base_frequency[0]),
                'DataGenerator.validate_base_frequency')
        if not isinstance(base_frequency[1], int):
            raise ConfigFileException(
                'Incrementation ({0}) must be an int'.format(base_frequency[1]),
                'DataGenerator.validate_base_frequency')

    def validate_num_to_generate(self, property, value):
        if not isinstance(value, int):
            raise ConfigFileException(
                '{0} ({1}) must be an int'.format(
                    property,
                    value),
                'DataGenerator.validate_num_to_generate')

    def validate_seeds(self, seeds):
        if not seeds == "timestamp":
            if not len(seeds[1]) == 2:
                raise ConfigFileException(
                    'seeds ({0}) distribution must contain 2 ints'.format(
                        seeds),
                    'DataGenerator.validate_seeds')
            elif not all(isinstance(x, int) for x in seeds):
                raise ConfigFileException(
                    'seeds ({0}) distribution must be of type int'.format(
                        seeds),
                    'DataGenerator.validate_seeds')

    def validate_distribution_schema(self, property, value):
        # perc_sum = 0
        for x in value:
            if len(x) != 2:
                raise ConfigFileException(
                    'The format of each field must be [int/float, [int/float(, int/float)]] where paranthesized values are optional.'.format(
                        property,
                        x[1]),
                    'DataGenerator.validate_json_range')
            elif not 1 <= len(x[1]) <= 2:
                raise ConfigFileException(
                    '{0} ({1}) distribution must contain 1 or 2 values.'.format(
                        property,
                        x[1]),
                    'DataGenerator.validate_json_range')
            elif not isinstance(x[0], (int, float)) or not all(isinstance(y, (int, float)) for y in x[1]):
                raise ConfigFileException(
                    '{0} ({1}) distribution and percentage must only contain ints or floats.'.format(
                        property,
                        x),
                    'DataGenerator.validate_json_range')
            elif x[0] < 0:
                raise ConfigFileException(
                    '{0} ({1}) percentage must be >= 0.'.format(
                        property,
                        x[0]),
                    'DataGenerator.validate_json_range')
            elif not all(y >= 0 for y in x[1]):
                raise ConfigFileException(
                    '{0} ({1}) distribution must contain values >= 0.'.format(
                        property,
                        x[1]),
                    'DataGenerator.validate_json_range')
            # perc_sum += x[0]
        # Floating arithmetic issues. Still need to figure out a good way to do this. Rounding?
        # if perc_sum != 1:
        #     raise ConfigFileException(
        #         '{0} ({1}) Sum of percentages must be equal to 1.'.format(
        #             property,
        #             perc_sum),
        #         'DataGenerator.validate_json_range')
