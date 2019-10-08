"""average.py

Class to hold the average values for the three metrics we're tracking in
CP1; value, bandwidth efficiency and number of TAs scheduled.

Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.processing.schedule import Schedule


class Average():
    def __init__(self, type):
        """Constructor

           For each type of Challenge Problem instance, one average class is maintained.
           At the bare minimum, there should be one instance of this class representing
           the unperturbed solution value for a CP instance. If perturbations have been
           applied to that instance, multiple instances will be created to track the
           relevant metrics (Number of TAs scheduled, Value, Average Bandwidth Efficiency).

       :param str type: The type of Challenge Problem instance this is for.
        """
        self.type = type
        # [Number of TAs, Optimizer Result Value, Average Bandwidth Efficiency for available channels]
        self.lower_bound = [0, 0, 0]
        self.cra_cp1 = [0, 0, 0]
        self.upper_bound = [0, 0, 0]

    def update(self, lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules):
        """Increments the values in the dictionary.

        :param OptimizerResult lower_bound_or: The Greedy Algorithm optimizer result
        :param [<Schedule>] lower_bound_schedules: The ConservativeScheduler run on the lower_bound_or
        :param OptimizerResult cra_cp1_or: The CRA CP1 IntegerProgram optimizer result
        :param [<Schedule] cra_cp1_schedules: The HybridScheduler run on the optimized_or
        :param OptimizerResult upper_bound_or: The IntegerProgram solved without a latency requirement optimizer result
        :param [<Schedule>] upper_bound_schedules: The HybridScheduler run on the upper_bound_or
        """
        self.lower_bound[0] += len(lower_bound_or.scheduled_tas)
        self.cra_cp1[0] += len(cra_cp1_or.scheduled_tas)
        self.upper_bound[0] += len(upper_bound_or.scheduled_tas)

        self.lower_bound[1] += lower_bound_or.value
        self.cra_cp1[1] += cra_cp1_or.value
        self.upper_bound[1] += upper_bound_or.value

        self.lower_bound[2] += (sum([schedule.compute_bw_efficiency() for schedule in lower_bound_schedules]) / len(lower_bound_schedules))
        self.cra_cp1[2] += (sum([schedule.compute_bw_efficiency() for schedule in cra_cp1_schedules]) / len(cra_cp1_schedules))
        self.upper_bound[2] += (sum([schedule.compute_bw_efficiency() for schedule in upper_bound_schedules]) / len(upper_bound_schedules))

    def compute(self, total_runs):
        """Computes the averages from the total number of runs.

        :param int total_runs: The total number of runs the start script went through
        """
        self.lower_bound[0] = self.lower_bound[0] / total_runs
        self.lower_bound[1] = self.lower_bound[1] / total_runs
        self.lower_bound[2] = self.lower_bound[2] / total_runs

        self.cra_cp1[0] = self.cra_cp1[0] / total_runs
        self.cra_cp1[1] = self.cra_cp1[1] / total_runs
        self.cra_cp1[2] = self.cra_cp1[2] / total_runs

        self.upper_bound[0] = self.upper_bound[0] / total_runs
        self.upper_bound[1] = self.upper_bound[1] / total_runs
        self.upper_bound[2] = self.upper_bound[2] / total_runs
