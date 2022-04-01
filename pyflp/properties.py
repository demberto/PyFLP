import abc
from typing import TYPE_CHECKING, Any, NoReturn

from pyflp.exceptions import OperationNotPermittedError
from pyflp.validators import (
    _BoolValidator,
    _BytesValidator,
    _ColorValidator,
    _EnumValidator,
    _FloatValidator,
    _IntValidator,
    _StrValidator,
    _UIntValidator,
)

if TYPE_CHECKING:
    from pyflp.flobject import _FLObject
    from pyflp.validators import _Validator


class _Property(abc.ABC):
    """Base class for property descriptors used in `FLObject` subclasses.

    https://stackoverflow.com/a/69599069"""

    def __init__(self, validator: "_Validator"):
        self.validator = validator

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} "
            f'name="{self.public_name}", '
            f'validator="{repr(self.validator)}">'
        )

    def __set_name__(self, owner, name: str):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, obj: "_FLObject", objtype=None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __delete__(self, obj) -> NoReturn:
        raise OperationNotPermittedError("Properties cannot be deleted", obj)

    def __set__(self, obj: "_FLObject", value) -> None:
        self.validator.validate(value)
        setattr(obj, self.private_name, value)

        # This allows for overriding setter logic in FLObject
        # subclass while still allowing to use these descriptors
        obj._setprop(self.public_name, value)


class _BoolProperty(_Property):
    def __init__(self):
        super().__init__(_BoolValidator())


class _BytesProperty(_Property):
    def __init__(self):
        super().__init__(_BytesValidator())


class _EnumProperty(_Property):
    def __init__(self, enum):
        super().__init__(_EnumValidator(enum))


class _FloatProperty(_Property):
    def __init__(self, validator=None):
        if validator is None:
            validator = _FloatValidator()
        super().__init__(validator)


class _IntProperty(_Property):
    def __init__(self, validator=None):
        if validator is None:
            validator = _IntValidator()
        super().__init__(validator)


class _StrProperty(_Property):
    def __init__(self, validator=None):
        if validator is None:
            validator = _StrValidator()
        super().__init__(validator)


class _UIntProperty(_Property):
    def __init__(self, validator=None):
        if validator is None:
            validator = _UIntValidator()
        super().__init__(validator)


class _ColorProperty(_Property):
    def __init__(self):
        super().__init__(_ColorValidator())
