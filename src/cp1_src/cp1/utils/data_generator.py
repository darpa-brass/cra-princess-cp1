"""data_generator.py

Interface for all data generators.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import abc
import random

class DataGenerator(abc.ABC):
    def _generate_within_ranges(self, ranges):
        """
        Takes in a set of ranges and produces one value for each range. If
        either of the two numbers in the range are a float, it will produce a
        float.

        :param [[]] ranges: The list of ranges for a variable.

        :return [] vals: One value generated for each range.
        """
        vals = []
        for i in range(0, len(ranges)):
            if len(ranges[i]) == 1:
                vals.append(ranges[i][0])
            else:
                if isinstance(ranges[i][0], float) or isinstance(ranges[i][1], float):
                    vals.append(random.uniform(
                        ranges[i][0], ranges[i][1]))
                else:
                    vals.append(random.randint(
                        ranges[i][0], ranges[i][1]
                    ))
        return vals

    @abc.abstractmethod
    def _validate(self):
        pass

    @abc.abstractmethod
    def generate(self, num):
        pass

    @abc.abstractmethod
    def generate_uniformly(self, num):
        pass
