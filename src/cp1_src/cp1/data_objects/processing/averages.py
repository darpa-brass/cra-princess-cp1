class Averages():
    def __init__(self):
        self.averages = {}
        self.averages['Minimum Bandwidth'] = [0, 0, 0]
        self.averages['Channel Dropoff'] = [0, 0, 0]
        self.averages['Channel Capacity'] = [0, 0, 0]
        self.averages['Perturbations'] = [0, 0, 0]
        self.averages['Lower Bound'] = 0
        self.averages['Optimized'] = 0
        self.averages['Upper Bound'] = 0

    def update(self, perturber, optimizer_result, unadapted_value, lower_bound_value, upper_bound_value):
        if perturber is not None:
            perturbation_bandwidth = sum(ta.bandwidth.value for ta in optimizer_result.scheduled_tas)
            if perturber.combine == 1:
                    self.averages['Perturbations'][1] = optimizer_result.value
                    self.averages['Perturbations'][2] = unadapted_value
            else:
                if perturber.ta_bandwidth != 0:
                    self.averages['Minimum Bandwidth'][1] += optimizer_result.value
                    self.averages['Minimum Bandwidth'][2] += unadapted_value
                elif perturber.channel_dropoff > 0:
                    self.averages['Channel Dropoff'][1] += optimizer_result.value
                    self.averages['Channel Dropoff'][2] += unadapted_value
                elif perturber.channel_capacity != 0:
                    self.averages['Channel Capacity'][1] += optimizer_result.value
                    self.averages['Channel Capacity'][2] += unadapted_value
        else:
            self.averages['Lower Bound'] += lower_bound_value
            self.averages['Optimized'] += optimizer_result.value
            self.averages['Upper Bound'] += upper_bound_value

    def update_unperturbed(self, lower_bound, combined):
        unperturbed_lower_bound_value = lower_bound.value # DO something with this
        if combined:
            self.averages['Perturbations'][0] += unperturbed_lower_bound_value
        else:
            self.averages['Minimum Bandwidth'][0] += unperturbed_lower_bound_value
            self.averages['Channel Dropoff'][0] += unperturbed_lower_bound_value
            self.averages['Channel Capacity'][0] += unperturbed_lower_bound_value

    def compute(self, total_runs):
        for average_type, average_value in self.averages.items():
            if isinstance(average_value, list):
                self.averages[average_type] = list(map(lambda x: x / total_runs, average_value))
            else:
                self.averages[average_type] = average_value / total_runs
