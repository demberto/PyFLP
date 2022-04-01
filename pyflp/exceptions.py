class Error(Exception):
    """Base class for PyFLP exceptions"""

    def __init__(self, what: str, *args: object) -> None:
        self.__what = what
        super().__init__(*args)

    def __repr__(self) -> str:
        return f"{type(self).__doc__}: {self.__what}"

    __str__ = __repr__


class DataCorruptionDetectedError(Error):
    """Possible corruption in event data detected"""


class InvalidHeaderSizeError(Error):
    """Invalid header size"""

    def __init__(self, size: int) -> None:
        super().__init__(size)


class InvalidMagicError(Error):
    """Invalid header magic number"""


class OperationNotPermittedError(Error):
    """Operation not permitted"""


class MaxInstancesError(Error):
    """Maximum number of instances already initialised"""

    def __init__(self, flobject_t):
        self.__type = flobject_t.__name__
        self.__max_count = flobject_t.max_count

    def __repr__(self) -> str:
        return f"{self.__type}: {self.__max_count} instances already initialised."
