"""accuracy_discretization.py

Provides a gurantee on the accuracy of the overall solution in relation to the optimal solution.
Guaranteed accuracy is: 1 - accuracy
i.e. accuracy = 0.001, therefore guaranteed accuracy is 99.999
num_discretizations = (1 - 0.001) * (100 / ta.utility_threshold)

Author: Tameem Samawi (tsamawi@cra.com)
"""

#it seems confusing to call the parameter of interest accuracy and that guaranteed accuracy is 1 - accuracy
#perhaps we replace accuracy with epsilon and accuracy = 1 - epsilon... just a thought

import math
from cp1.processing.algorithms.discretization.discretization_strategy import DiscretizationStrategy

############ Old stuff.  Tyler redo after thinking more about this

# class AccuracyDiscretization(DiscretizationStrategy):
#     def __init__(self, accuracy):
#         self.accuracy = accuracy

#     def discretize(self, constraints_object):
#         tas = []
#         for ta in constraints_object.candidate_tas:
#             for channel in constraints_object.channels:
#                 num_discretizations = math.ceil((1 / self.accuracy) * \
#                     (100 / ta.utility_threshold))
#                 interval_size = (100 - ta.utility_threshold) / \
#                     num_discretizations
#                 for i in range(0, num_discretizations):
#                     value = ta.utility_threshold + interval_size * i
#                     tas.append(
#                         [ta, ta.compute_bandwidth(value), value, channel.frequency.value])
#         return tas

#     def discretize_one_channel(self, constraints_object):
#             return



class AccuracyDiscretization(DiscretizationStrategy):
    def __init__(self, accuracy):
        self.accuracy = accuracy
        #Tyler added this because it wasn't being recognized as an attirbute of the class in methods which use it
        self.num_discretizations = 0

    def discretize(self, constraints_object):
        tas = []
        # find the minimum  utility threshold among all TAs
        min_utility_threshold = 100
        for ta in constraints_object.candidate_tas:
            if min_utility_threshold > ta.utility_threshold/ta.scaling_factor:
                min_utility_threshold = ta.utility_threshold/ta.scaling_factor

        #file = open("accuracy disc output", "a")
        #file.write('minimum utility: {0}\n'.format(min_utility_threshold))
        #compute num_discretizations -- needs to be the same for all TAs
        self.num_discretizations = math.ceil(math.log(min_utility_threshold/100)/math.log(1 - self.accuracy))

        #The actual samples (on y axis) for each TA should be taken as the following geometric sequence
        # 100, (1 - accuracy)100, (1 - accuracy)^2*100, ..., (1 - accuracy)^{num_discretizations}100
        #with the caviat that if (1 - accuracy)^k*100 < ta.utility_threshold then just take ta.utility threshold to avoid 0 value samples (this can be reworked later.)
        for ta in constraints_object.candidate_tas:
            #file.write('ta {0}, min bw {1}, min val {2}, min util {3}, scaling factor {4} \n'.format(ta.id_, ta.total_minimum_bandwidth.value, ta.utility_threshold, ta.utility_threshold/ta.scaling_factor, ta.scaling_factor))
            for channel in constraints_object.channels:
                for i in range(0, self.num_discretizations):
                    perc_value = 100*math.pow((1 - self.accuracy), i)
                    #file.write('\t val for ta {0} = {1}\n'.format(ta.id_, perc_value))
                    if perc_value < ta.utility_threshold/ta.scaling_factor:
                        tas.append([ta, ta.compute_value(ta.total_minimum_bandwidth.value), ta.total_minimum_bandwidth.value, channel.frequency.value])
                        #file.write('if pushed: id: {0}, val: {1}, bw: {2}, chan: {3}\n'.format(ta.id_, ta.compute_value(ta.total_minimum_bandwidth.value), ta.total_minimum_bandwidth.value, channel.frequency.value))                
                    else:
                         tas.append([ta, perc_value*ta.scaling_factor, ta.compute_bandwidth(perc_value),channel.frequency.value])
                        # file.write('else pushed: id: {0}, val: {1}, bw: {2}, chan: {3}\n'.format(ta.id_, perc_value*ta.scaling_factor, ta.compute_bandwidth(perc_value), channel.frequency.value))                

        
        #for i in range (0, len(tas)):
            #file.write('id: {0}, val: {1}, bw: {2}, chan: {3}\n'.format(tas[i][0].id_, tas[i][1], tas[i][2], tas[i][3]))
        
        #file.close()
        return tas

    def discretize_one_channel(self, constraints_object):  
        tas = []
        # find the minimum  utility threshold among all TAs
        min_utility_threshold = 100
        for ta in constraints_object.candidate_tas:
            if min_utility_threshold > ta.utility_threshold/ta.scaling_factor:
                min_utility_threshold = ta.utility_threshold/ta.scaling_factor

        self.num_discretizations = math.ceil(math.log(min_utility_threshold/100)/math.log(1 - self.accuracy))
       
        for ta in constraints_object.candidate_tas:
            for i in range(0, self.num_discretizations):
                perc_value = 100*math.pow((1 - self.accuracy), i)
                if perc_value < ta.utility_threshold/ta.scaling_factor:
                    tas.append([ta, ta.compute_value(ta.total_minimum_bandwidth.value), ta.total_minimum_bandwidth.value])
                else:
                    tas.append([ta, perc_value*ta.scaling_factor, ta.compute_bandwidth(perc_value)])

        return tas 
