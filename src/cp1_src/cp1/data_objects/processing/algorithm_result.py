"""algorithm_result.py

Data object to encapsulate algorithm results.
Author: Tameem Samawi (tsamawi@cra.com)
"""
import csv


class AlgorithmResult:
    def __init__(self, scheduled_tas, solve_time, run_time, value):
        """
        Constructor

        :param List[TA] scheduled_tas: New schedule outputted by algorithm.
        :param int solve_time: Time taken to generate schedule, does not include any of the setup.
                               For integer programs, this is the time it takes solver.solve() to run.
                               For the greedy algorithm, this is the same as the solve_time since there is
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

    __repr__ = __str__
