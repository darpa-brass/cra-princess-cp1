"""timedelta.py

Wrapper to allow the milliseconds of a datetime to be retrieved. Only works
if milliseconds has been explicitly set, does not support conversions.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from datetime import timedelta as timedelta_

class timedelta(timedelta_):
    def __init__(self, *args, **kwargs):
        self.milliseconds = kwargs.get('milliseconds')
        super(timedelta, self).__init__()
