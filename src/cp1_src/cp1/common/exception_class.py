"""exception_class.py

Module contains custom exception classes.
Author: Tameem Samawi(tsamawi@cra.com)
"""


class ChannelGeneratorException(ValueError):
    """Raise for inavalid values passed into the ChannelGenerator.generate() function"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ChannelGeneratorException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class DeadlineCompetitionException(ValueError):
    """Raise for too many TAs competing to communicate within the same communication block."""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(DeadlineCompetitionException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)

class PercentageRangeFormatException(ValueError):
    """Raise for invalid PRF fields"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(PercentageRangeFormatException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidNumToGenerateException(ValueError):
    """Raise when the number of objects to generate is invalid in any DataGenerator class"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(InvalidNumToGenerateException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidSeedException(ValueError):
    """Raise for invalid seeds to generate fields"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(InvalidSeedException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class InvalidLatencyRequirementException(ValueError):
    """Raise for TAs whose latency requirements exceed half the MDL epoch"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(InvalidLatencyRequirementException, self).__init__(message)
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


class SchedulingJobInitializationException(ValueError):
    """Raise for SchedulingJob initializations"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(SchedulingJobInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class RadioLinkNotFoundException(ValueError):
    """Raise for TxOp initializations"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(RadioLinkNotFoundException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class MACAddressParseError(ValueError):
    """Raise for exceptions in parsing SwRIs naming scheme for MAC Addresses"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(MACAddressParseError, self).__init__(message)
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


class ChannelsNotFoundException(Exception):
    """Raise for general responses that come back empty"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ChannelsNotFoundException, self).__init__(message)
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


class ScheduleInitializationException(ValueError):
    """Raise for invalid schedule initializations"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ScheduleInitializationException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ComputeValueException(ValueError):
    """Raise for invalid TA.compute_value inputs"""

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


class ComputeBandwidthException(ValueError):
    """Raise for invalid TA.compute_bandwidth inputs"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ComputeBandwidthException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)


class ConfigFileException(ValueError):
    """Raise for invalid TA.compute_bandwidth inputs"""

    def __init__(self, message, source=''):
        """Constructor

        :param str message:     Exception message
        :param str source:      Which function threw the exception
        """
        super(ConfigFileException, self).__init__(message)
        self.message = message
        self.source = source

    def __str__(self):
        return "[EXCEPTION] {0} [SOURCE] {1}\n".format(
            self.message, self.source)
