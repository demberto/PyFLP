__all__ = ["DataCorruptionDetected"]


class Error(Exception):
    """Base class for all PyFLP exceptions"""

    def __init__(self, msg: str, *args: object) -> None:
        self.__msg = msg
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{self.__class__.__doc__} {self.__msg}"


class DataCorruptionDetected(Error):
    """Possible corruption in event data detected"""


class OperationNotPermitted(Error):
    """Operation not permitted"""
