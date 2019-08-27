"""timedelta.py

Wrapper to allow the milliseconds of a datetime to be retrieved. Only works
if milliseconds has been explicitly set, does not support conversions.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from datetime import timedelta as timedelta_

class timedelta(timedelta_):
    def __init__(self, *args, **kwargs):
        super(timedelta, self).__init__()

    def get_milliseconds(self):
        return int(self.microseconds / 1000)
