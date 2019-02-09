from cp1.processing.algorithm import optimize


class ProcessConstraints:
    def process(constraints_object):
        new_schedule = optimize(constraints_object)
        
