import abc
import enum
from typing import Any, Iterable, Optional, Type, Union

import colour

from pyflp.utils import isascii


class _Validator(abc.ABC):
    """Base class of all validator classes."""

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    @abc.abstractmethod
    def validate(self, value: Any):
        pass


class _OneOfValidator(_Validator):
    """Validates whether a value exists in a given set of options."""

    def __init__(self, options: Iterable):
        self.options = options

    def __repr__(self) -> str:
        return f"<{type(self).__name__} options={self.options}>"

    def validate(self, value: Any):
        if value not in self.options:
            raise ValueError(f"Expected {value!r} to be one of {self.options!r}")


class _BoolValidator(_OneOfValidator):
    """Validates whether a value equals `True` or `False`."""

    def __init__(self):
        super().__init__((True, False))

    def __repr__(self) -> str:
        return "<BoolValidator>"

    def validate(self, value: Any):
        if not isinstance(value, bool):
            raise TypeError(f"Expected {value!r} to be a bool")


class _EnumValidator(_OneOfValidator):
    """Validates whether a value exists in a particular `enum` class."""

    _Enum = Union[Type[enum.Enum], Type[enum.IntEnum], Type[enum.IntFlag]]

    def __init__(self, enum: _Enum):
        self.enum = enum
        super().__init__(tuple(enum))

    def __repr__(self) -> str:
        return f'<EnumValidator enum="{self.enum.__name__}>"'


class _IntFloatValidatorBase(_Validator):
    """Base class for `_IntValidator` and `_FloatValidator`."""

    def __init__(self, _min, _max) -> None:
        self.min = _min
        self.max = _max

    def __repr__(self) -> str:
        return f"<{type(self).__name__} min={self.min}, max={self.max}>"


class _IntValidator(_IntFloatValidatorBase):
    """Validates whether value is an `int` and lies in a range, optionally."""

    def __init__(self, min: Optional[int] = None, max: Optional[int] = None):
        self.min = min
        self.max = max

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise TypeError(f"Expected {value!r} to be an int")
        if self.min is not None and value < self.min:
            raise ValueError(f"Expected {value!r} to be at least {self.min!r}")
        if self.max is not None and value > self.max:
            raise ValueError(f"Expected {value!r} to be no more than {self.max!r}")


class _UIntValidator(_IntValidator):
    """A specialization of `_IntValidator` for validating positive integers."""

    def __init__(self, max: Optional[int] = None):
        super().__init__(min=0, max=max)


class _FloatValidator(_IntFloatValidatorBase):
    """Validates whether value is an `float` and lies in a range, optionally."""

    def __init__(
        self, min: Optional[float] = None, max: Optional[float] = None
    ) -> None:
        self.min = min
        self.max = max

    def validate(self, value: Any):
        if not isinstance(value, float):
            raise TypeError(f"Expected {value!r} to be a float")
        if self.min is not None and value < self.min:
            raise ValueError(f"Expected {value!r} to be at least {self.min!r}")
        if self.max is not None and value > self.max:
            raise ValueError(f"Expected {value!r} to be no more than {self.max!r}")


class _BytesStrValidatorBase(_Validator):
    """Base class for `_BytesValidator` and `_StrValidator`."""

    def __init__(self, minsize: Optional[int] = None, maxsize: Optional[int] = None):
        self.minsize = minsize
        self.maxsize = maxsize

    def __repr__(self) -> str:
        return f"<{type(self).__name__} min={self.minsize}, max={self.maxsize}>"

    def validate(self, value: Any):
        if self.minsize is not None and len(value) < self.minsize:
            raise ValueError(
                f"Expected {value!r} to be no smaller than {self.minsize!r}"
            )
        if self.maxsize is not None and len(value) > self.maxsize:
            raise ValueError(
                f"Expected {value!r} to be no bigger than {self.maxsize!r}"
            )


class _BytesValidator(_BytesStrValidatorBase):
    """Validates the type and size of a `bytes` object."""

    def validate(self, value: Any):
        if not isinstance(value, bytes):
            raise TypeError(f"Expected {value!r} to be a bytes object")
        super().validate(value)


class _StrValidator(_BytesStrValidatorBase):
    """Validates the type and size of an `str` object."""

    def __init__(
        self,
        minsize: Optional[int] = None,
        maxsize: Optional[int] = None,
        mustascii: bool = False,
    ):
        super().__init__(minsize, maxsize)
        self.mustascii = mustascii

    def validate(self, value: Any):
        if not isinstance(value, str):
            raise TypeError(f"Expected {value!r} to be an str")
        if self.mustascii and not isascii(value):
            raise TypeError(f"Expected {value!r} to be an ASCII string")
        super().validate(value)


class _ColorValidator(_Validator):
    """Validates whether the type of value is `colour.Color`."""

    def validate(self, value: Any):
        if not isinstance(value, colour.Color):
            raise TypeError(f"Expected {value!r} to be a {type(colour.Color)} object")
