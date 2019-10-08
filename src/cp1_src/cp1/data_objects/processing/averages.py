"""averages.py

A class for managing the averages maintained during execution of CP1.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.data_objects.processing.average import Average


class Averages():
    def __init__(self):
        """Constructor
        """
        self.averages = {}
        average_types = ['Unperturbed', 'Combined Perturbations', 'Minimum Bandwidth',
                        'Channel Capacity', 'Channel Dropoff']
        for type in average_types:
            self.averages[type] = Average(type)

    def update(self, perturber, lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules):
        """
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

        self.averages[type].update(lower_bound_or, lower_bound_schedules, cra_cp1_or, cra_cp1_schedules, upper_bound_or, upper_bound_schedules)

    def compute(self, total_runs):
        for type, average in self.averages.items():
            average.compute(total_runs)
