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
        return int((self / timedelta_(microseconds=1) / 1000))

    def get_microseconds(self):
        return int(self/timedelta_(microseconds=1))

    def __add__(self, other):
        timedelta_result = super(timedelta, self).__add__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    __radd__ = __add__

    def __sub__(self, other):
        timedelta_result = super(timedelta, self).__sub__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __rsub__(self, other):
        timedelta_result = super(timedelta, self).__rsub__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __neg__(self):
        timedelta_result = super(timedelta, self).__neg__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    # def __truediv__(self, other):
    #     timedelta_result = super(timedelta, self).__truediv__(other)
    #     return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __mod__(self, other):
        timedelta_result = super(timedelta, self).__mod__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __divmod__(self, other):
        timedelta_result = super(timedelta, self).__divmod__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __floordiv__(self, other):
        timedelta_result = super(timedelta, self).__floordiv__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    def __mul__(self, other):
        timedelta_result = super(timedelta, self).__mul__(other)
        return timedelta(days=timedelta_result.days, seconds=timedelta_result.seconds, microseconds=timedelta_result.microseconds)

    __rmul__ = __mul__
