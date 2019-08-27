"""optimizer_result.py

Data object to encapsulate algorithm results.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import csv


class OptimizerResult:
    def __init__(self, scheduled_tas, solve_time, run_time, value):
        """
        Constructor

        :param {Channel: [<TA>]} scheduled_tas: New schedule outputted by algorithm.
        :param {Channel: int} bw_eff: The bandwidth efficiency of each channel
        :param int solve_time: Time taken to generate schedule, does not include any of the setup.
                               For integer programs, this is the time it takes solver.solve() to run.
                               For the greedy optimization, this is the same as the solve_time since there is
                               no pre-processing.
        :param int run_time: Time taken to run the algorithm from start to finish.
        :param int value: The value of the new schedule.
        """
        self.scheduled_tas = scheduled_tas
        self.solve_time = solve_time
        self.run_time = run_time
        self.value = value

    def __str__(self):
        return 'scheduled_tas: {0}, solve_time: {1}, run_time: {2}, value: {3}'.format(self.scheduled_tas, self.solve_time, self.run_time, self.value)

    def get_scheduled_tas_as_list(self):
        """ Returns a list representation of the dictionary of scheduled_tas

        :returns [<TA>] ta_list: The list of scheduled TAs
        """
        ta_list = []
        for channel, tas_scheduled_on_channel in self.scheduled_tas.items():
            for ta in tas_scheduled_on_channel:
                ta_list.append(ta)

        return ta_list

    __repr__ = __str__
