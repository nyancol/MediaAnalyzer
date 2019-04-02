class MediaAnalyzerException(Exception):
    """Abstract exception class"""


class InvalidTwitterUserException(MediaAnalyzerException):
    """Invalid Twitter screen name"""


class DuplicateDBEntryException(MediaAnalyzerException):
    """Entry already exist in DB"""


class RabbitMQException(MediaAnalyzerException):
    def __init__(self, message):
        super(RabbitMQException, self).__init__(message)


class DatabaseConnectionError(MediaAnalyzerException):
    """Unable to connect to the Database"""
    def __init__(self, message):
        super(DatabaseConnectionError, self).__init__(message)
