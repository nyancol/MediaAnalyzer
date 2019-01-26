class MediaAnalyzerException(Exception):
    """Abstract exception class"""


class InvalidTwitterUserException(MediaAnalyzerException):
    """Invalid Twitter screen name"""


class DuplicateDBEntryException(MediaAnalyzerException):
    """Entry already exist in DB"""
