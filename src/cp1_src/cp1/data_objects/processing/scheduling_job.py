"""scheduling_job.py

Data Object to house an OS Scheduling job.
"""
from datetime import timedelta
from cp1.common.exception_class import SchedulingJobInitializationException

class SchedulingJob:
    def __init__(self, ta, job_length, start_deadline, release_date, direction):
        '''
        Constructor

        :param TA ta: The TA this job is for
        :param timedelta job_length: The length of the job
        :param timedelta start_deadline: The time by which this job must begin in order to meet the TAs latency requirement
        :param timedelta release_date: The time by which this job is eligible to be considered by the scheduler
        :param str direction: Direction of the SchedulingJob, up or down
        '''
        if not isinstance(job_length, timedelta):
            raise SchedulingJobInitializationException('job_length ({0}) must be an instance of timedelta'.format(type(job_length)))
        if not isinstance(start_deadline, timedelta):
            raise SchedulingJobInitializationException('start_deadline ({0}) must be an instance of timedelta'.format(type(start_deadline)))
        if not isinstance(release_date, timedelta):
            raise SchedulingJobInitializationException('release_date ({0}) must be an instance of timedelta'.format(type(release_date)))
        if not isinstance(direction, str):
            raise SchedulingJobInitializationException('direction ({0}) must be an instance of Boolean'.format(type(direction)))
        self.ta = ta
        self.job_length = job_length
        self.start_deadline = start_deadline
        self.release_date = release_date
        self.direction = direction

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
