import csv
from cp1.utils.ta_generator import TAGenerator
from ortools.linear_solver import pywraplp
from cp1.utils.channel_generator import ChannelGenerator
from cp1.data_objects.mdl.kbps import Kbps
from cp1.data_objects.processing.constraints_object import ConstraintsObject
from cp1.processing.algorithms.discretization.accuracy_discretization import AccuracyDiscretization
from cp1.processing.algorithms.discretization.bandwidth_discretization import BandwidthDiscretization
from cp1.processing.algorithms.optimization.gurobi import Gurobi
from cp1.processing.algorithms.optimization.dynamic_program import DynamicProgram
from cp1.processing.algorithms.optimization.integer_program import IntegerProgram


# values = [2, 4, 8, 16, 32, 64]
accuracies = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
gurobi_res = []
cbc_res = []
for seed in range(1, 10):
    for j in accuracies:
        # Setup data
        ta_generator = TAGenerator(seed=seed)
        candidate_tas = ta_generator.generate(10)
        channel_generator = ChannelGenerator(seed=seed)
        channels = channel_generator.generate(2)
        constraints_object = ConstraintsObject(candidate_tas=candidate_tas, channels=channels)
        discretization_algorithm = AccuracyDiscretization(1-j)

        # Run algorithm
        cbc = IntegerProgram(constraints_object)
        cbc_res = cbc.optimize(discretization_algorithm)

        gurobi = Gurobi(constraints_object)
        gurobi_res = gurobi.optimize(discretization_algorithm)

        with open('gurobi_res.csv', 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([seed, j, gurobi_res.value, gurobi_res.run_time])

        with open('cbc_res.csv', 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([seed, j, cbc_res.value, cbc_res.run_time])
