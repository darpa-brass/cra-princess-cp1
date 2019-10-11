"""averages.py

Classes to hold and maintain the average values for the three metrics we're tracking in
CP1; value, bandwidth efficiency and number of TAs scheduled.

Author: Tameem Samawi (tsamawi@cra.com)
"""
from typing import List
from cp1.data_objects.processing.schedule import Schedule
from cp1.data_objects.processing.optimizer_result import OptimizerResult
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.data_objects.processing.perturber import Perturber
from cp1.common.logger import Logger

logger = Logger().logger


class Averages():
    UNPERTURBED_AVERAGE = 'Unperturbed'
    COMBINED_PERTURBED_AVERAGE = 'Combined Perturbations'
    PERTURBED_AVERAGES = ['Minimum Bandwidth', 'Channel Capacity', 'Channel Dropoff']

    def __init__(self):
        """Constructor.

           Sets up one average class per average type defined
        """
        _average_types =  [self.UNPERTURBED_AVERAGE] + [self.COMBINED_PERTURBED_AVERAGE] + self.PERTURBED_AVERAGES
        self.averages = {}
        for type in _average_types:
            self.averages[type] = self.Average(type)

    def update(self,
        constraints_object: ConstraintsObject,
        perturber: Perturber,
        lower_bound_or: OptimizerResult,
        lower_bound_schedules: List[Schedule],
        cra_cp1_or: OptimizerResult,
        cra_cp1_schedules: List[Schedule],
        upper_bound_or: OptimizerResult,
        upper_bound_schedules: List[Schedule]) -> None:
        """Updates only the relevant average type based on the data passed in.

        :param ConstraintsObject constraints_object: The Constraints Object used in this instance
        :param Perturbed perturber: The perturbed used in this run
        :param OptimizerResult lower_bound_or: The Greedy Algorithm optimizer result
        :param [<Schedule>] lower_bound_schedules: The ConservativeScheduler run on the lower_bound_or
        :param OptimizerResult cra_cp1_or: The CRA CP1 IntegerProgram optimizer result
        :param [<Schedule] cra_cp1_schedules: The HybridScheduler run on the optimized_or
        :param OptimizerResult upper_bound_or: The IntegerProgram solved without a latency requirement optimizer result
        :param [<Schedule>] upper_bound_schedules: The HybridScheduler run on the upper_bound_or
        """
        if perturber is None:
            type = 'Unperturbed'
        else:
            if perturber.combine == 1:
                type = 'Combined Perturbations'
            else:
                if perturber.ta_bandwidth != 0:
                    type = 'Minimum Bandwidth'
                elif perturber.channel_dropoff > 0:
                    type = 'Channel Dropoff'
                elif perturber.channel_capacity != 0:
                    type = 'Channel Capacity'

        self.averages[type].update(constraints_object, lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules)

    def compute(self, total_runs):
        """Calls compute on all average classes.

        :param int total_runs: The total amount of runs
        """
        for type, average in self.averages.items():
            average.compute(total_runs)

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
            # [Number of TAs, Optimizer Result Value, Average Bandwidth Efficiency]
            self.lower_bound = [0, 0, 0]
            self.cra_cp1 = [0, 0, 0]
            self.upper_bound = [0, 0, 0]

        def update(self, constraints_object, lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules):
            """Increments the values in the dictionary.

            :param ConstraintsObject constraints_object: The Constraints Object used in this instance
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
            for i in range(3):
                self.lower_bound[i] = round(self.lower_bound[i] / total_runs, 2)
                self.cra_cp1[i] = round(self.cra_cp1[i] / total_runs, 2)
                self.upper_bound[i] = round(self.upper_bound[i] / total_runs, 2)
