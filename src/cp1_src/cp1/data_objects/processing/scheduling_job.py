"""scheduling_job.py

Data Object to house an OS Scheduling job.
"""
class SchedulingJob:
    def __init__(self, ta, job_length, start_deadline, release_date):
        '''
        Constructor

        :param TA ta: The TA this job is for
        :param int job_length: The length of the job in ms
        :param int start_deadline: The time by which this job must begin in order to meet the TAs latency requirement in ms
        :param int release_date: The time by which this job is eligible to be considered by the scheduler in ms
        '''
        self.ta = ta
        self.job_length = job_length
        self.start_deadline = start_deadline
        self.release_date = release_date

    def __str__(self):
        return '<ta: {0}, ' \
               'job_length: {1}, ' \
               'start_deadline: {2}, ' \
               'release_date: {3}>'.format(
                   self.ta,
                   self.job_length,
                   self.start_deadline,
                   self.release_date)

    __repr__ = __str__
