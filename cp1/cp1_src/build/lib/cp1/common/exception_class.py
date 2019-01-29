"""

exception_class.py

Module contains custom exception classes.

Author: Tameem Samawi(tsamawi@cra.com)
"""


class NodeNotFoundException(Exception):
    """ Raise for query responses that come back empty """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(NodeNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class BandwidthRateInitializationError(ValueError):
    """ Raise for attempted invalid BandwidthRate initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(BandwidthRateInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class BandwidthSetInitializationError(ValueError):
    """ Raise for attempted invalid BandwidthSet initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(BandwidthSetInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class FrequencyInitializationError(ValueError):
    """ Raise for attempted invalid Frequency initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(FrequencyInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpTimeoutInitializationError(ValueError):
    """ Raise for attempted invalid TxOpTimeout initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TxOpTimeoutInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class KbpsInitializationError(ValueError):
    """ Raise for attempted invalid Kbps initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(KbpsInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MdlIdInitializationError(ValueError):
    """ Raise for attempted invalid MdlId initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MdlIdInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MillisecondsInitializationError(ValueError):
    """ Raise for attempted invalid Milliseconds initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MillisecondsInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)

class MicrosecondsInitializationError(ValueError):
    """ Raise for attempted invalid Microseconds initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MicrosecondsInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpInitializationError(ValueError):
    """ Raise for attempted invalid TxOp initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TxOpInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class OptimizationResultInitializationError(ValueError):
    """ Raise for attempted invalid OptimizationResult initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(OptimizationResultInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ScheduleInitializationError(ValueError):
    """ Raise for attempted invalid Schedule initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ScheduleInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ScheduleAddError(ValueError):
    """ Raise for attempted invalid additions to the Schedule """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ScheduleAddError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class StoreResultInitializationError(ValueError):
    """ Raise for attempted invalid StoreResult initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(StoreResultInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class SystemWideConstraintsNotFoundError(ValueError):
    """ Raise when system wide constraints are not found in the database """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(SystemWideConstraintsNotFoundError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TAInitializationError(ValueError):
    """ Raise for attempted invalid TA initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TAInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ChannelInitializationError(ValueError):
    """ Raise for attempted invalid Channel initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ChannelInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ConstraintsObjectInitializationError(ValueError):
    """ Raise for attempted invalid Constraints Object initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ConstraintsObjectInitializationError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidScheduleError(ValueError):
    """ Raise for invalid schedules """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(InvalidScheduleError, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)
