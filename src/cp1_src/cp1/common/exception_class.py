"""exception_class.py

Module contains custom exception classes.
Author: Tameem Samawi(tsamawi@cra.com)
"""

class ChannelGeneratorRangeException(ValueError):
    """Raise for channel generators with invalid ranges"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ChannelGeneratorRangeException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpInitializationException(ValueError):
    """Raise for TxOp initializations"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(TxOpInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpTimeoutInitializationException(ValueError):
    """Raise for TxOpTimeout initializations"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(TxOpTimeoutInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class NodeNotFoundException(Exception):
    """Raise for general responses that come back empty"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(NodeNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TAsNotFoundException(Exception):
    """Raise for TA responses that come back empty"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(TAsNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TAGeneratorRangeException(ValueError):
    """Raise for attempted invalid TAGenerator initializations"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(TAGeneratorRangeException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ScheduleAddException(ValueError):
    """Raise for attempted invalid additions to the Schedule """
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ScheduleAddException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidAlgorithmException(ValueError):
    """Raise for unsupported algorithm selections"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(InvalidAlgorithmException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class SystemWideConstraintsNotFoundException(ValueError):
    """Raise when system wide constraints are not found in the database"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(SystemWideConstraintsNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ConstraintsNotFoundException(ValueError):
    """Raise when constraints are not found in the database"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ConstraintsNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidScheduleException(ValueError):
    """Raise for invalid schedules"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(InvalidScheduleException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ComputeValueException(ValueError):
    """Raise for invalid schedules"""
    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ComputeValueException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)
