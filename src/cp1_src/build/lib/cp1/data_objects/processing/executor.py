"""executor.py

An executor class that neatly stores all three algorithms, and runs them in one method.
"""


class Executor():
    def __init__(self, discretization_algorithm, optimization_algorithm, scheduling_algorithm):
        """
        :param DiscretizationAlgorithm discretization_algorithm: Any DiscretizationAlgorithm to discretize data
        :param OptimizationAlgorithm optimization_algorithm: Any OptimizationAlgorithm to optimize TAs
        :param SchedulingAlgorithm scheduling_algorithm: Any SchedulingAlgorithm to schedule the selected TAs
        """
        self.discretization_algorihtm = discretization_algorithm
        self.optimization_algorithm = optimization_algorithm
        self.scheduling_algorithm = scheduling_algorithm

    def execute():
        """
        Runs the three abstract methods; discretize(), optimize(), schedule()
        of each of the algorithms in succession.

        :returns TxOpSchedule txop_schedule: The newly constructed schedule
        """
        data = self.discretization_algorithm.discretize()
        algorithm_result = self.optimization_algorithm.optimize(data)
        txop_schedule = self.scheduling_algorithm.schedule(algorithm_result)

        return txop_schedule
