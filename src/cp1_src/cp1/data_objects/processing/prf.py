"""percentage_range_format.py

Class to hold and evaluate PRF objects.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import numpy
import random


class PRF():
    def __init__(self, prf):
        """Calls evaluate and returns the selected value

        :param [int, [int(, int)]] prf: The set of ranges associated with this percentage
        """
        self.prf = prf

    def evaluate(self):
        """
        Takes in a field from data_generator.json and generates one value for each range.
        If either of the two numbers in the range are a float, it will produce a
        float.

        :return int val: One value generated this PRF.
        """    
        percentages = []
        for x in self.prf:
            percentages.append(x[0])

        vals = []
        for i in range(0, len(self.prf)):
            if len(self.prf[i][1]) == 1:
                vals.append(self.prf[i][1][0])
            else:
                if isinstance(self.prf[i][1][0], float) or isinstance(self.prf[i][1][1], float):
                    vals.append(random.uniform(
                        self.prf[i][1][0], self.prf[i][1][1]))
                else:
                    vals.append(random.randint(
                        self.prf[i][1][0], self.prf[i][1][1]
                    ))

        selected_val = numpy.random.choice(vals, p=percentages)

        return selected_val
