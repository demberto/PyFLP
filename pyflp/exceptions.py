class Error(Exception):
    """Base class for PyFLP exceptions"""

    def __init__(self, what: str, *args: object) -> None:
        self.what = what
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{type(self).__doc__}: {self.what}"


class DataCorruptionDetectedError(Error):
    """Possible corruption in event data detected"""


class OperationNotPermittedError(Error):
    """Operation not permitted"""
