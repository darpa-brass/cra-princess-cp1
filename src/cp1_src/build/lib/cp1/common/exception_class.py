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


class TAsNotFoundException(Exception):
    """ Raise for query responses for TAs that come back empty """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TAsNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class AlgorithmInitializationException(Exception):
    """ Raise for attempted invalid Algorithm initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(AlgorithmInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ProcessBandwidthInitializationException(Exception):
    """ Raise for attempted invalid ProcessBandwidth initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ProcessBandwidthInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class BandwidthRateInitializationException(ValueError):
    """ Raise for attempted invalid BandwidthRate initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(BandwidthRatetInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class FrequencyInitializationException(ValueError):
    """ Raise for attempted invalid Frequency initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(FrequencyInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpTimeoutInitializationException(ValueError):
    """ Raise for attempted invalid TxOpTimeout initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TxOpTimeoutInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class KbpsInitializationException(ValueError):
    """ Raise for attempted invalid Kbps initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(KbpsInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MdlIdInitializationException(ValueError):
    """ Raise for attempted invalid MdlId initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MdlIdInitializationException, self).__init__(message)
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

class MicrosecondsInitializationException(ValueError):
    """ Raise for attempted invalid Microseconds initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MicrosecondsInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MillisecondsInitializationException(ValueError):
    """ Raise for attempted invalid Milliseconds initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MillisecondsInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MicrosecondsInitializationException(ValueError):
    """ Raise for attempted invalid Microseconds initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(MicrosecondsInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TxOpInitializationException(ValueError):
    """ Raise for attempted invalid TxOp initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TxOpInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class OptimizationResultInitializationException(ValueError):
    """ Raise for attempted invalid OptimizationResult initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(OptimizationResultInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ScheduleInitializationException(ValueError):
    """ Raise for attempted invalid Schedule initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ScheduleInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ScheduleAddException(ValueError):
    """ Raise for attempted invalid additions to the Schedule """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ScheduleAddException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class StoreResultInitializationException(ValueError):
    """ Raise for attempted invalid StoreResult initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(StoreResultInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class SystemWideConstraintsNotFoundException(ValueError):
    """ Raise when system wide constraints are not found in the database """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(SystemWideConstraintsNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class TAInitializationException(ValueError):
    """ Raise for attempted invalid TA initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(TAInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ChannelInitializationException(ValueError):
    """ Raise for attempted invalid Channel initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ChannelInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ConstraintsObjectInitializationException(ValueError):
    """ Raise for attempted invalid Constraints Object initializations """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(ConstraintsObjectInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidScheduleException(ValueError):
    """ Raise for invalid schedules """

    def __init__(self, message, source=''):
        """
        Constructor

        :param str message:     exception message
        :param str source:      which function threw the exception
        """
        super(InvalidScheduleException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)
