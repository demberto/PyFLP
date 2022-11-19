Developer Reference
===================

This page documents PyFLP's internals which consists of :mod:`pyflp._events`,
:mod:`pyflp._descriptors` and :mod:`pyflp._models`.

    The content below assumes you have fairly good knowledge of the following:

    - OOP and descriptors, especially
    - Type annotations
    - Binary data types and streams

Events
------

.. automodule:: pyflp._events

If you have read Part I, you know how events use a TLV encoding scheme.

Type
^^^^

The ``type`` represents the event ID. A custom enum class (and a metaclass)
supporting unknown IDs and member check using Python's ``... in ...`` syntax is
used.

.. autoclass:: _EventEnumMeta
   :members:
.. autoclass:: EventEnum
   :members:

Length
^^^^^^

The ``length`` is a field prefixed for IDs in the range of 192-255. It is the
size of ``value`` and is encoded as a VLQ128 (variable length quantity base-128).

Value
^^^^^

Below are the list of classes PyFLP has, grouped w.r.t the ID range.

.. dropdown:: 0-63

    .. autoclass:: ByteEventBase
    .. autoclass:: U8Event
    .. autoclass:: BoolEvent
    .. autoclass:: I8Event

.. dropdown:: 64-127

    .. autoclass:: WordEventBase
    .. autoclass:: U16Event
    .. autoclass:: I16Event

.. dropdown:: 128-191

    .. autoclass:: DWordEventBase
    .. autoclass:: U32Event
    .. autoclass:: I32Event
    .. autoclass:: ColorEvent
    .. autoclass:: U16TupleEvent

.. dropdown:: 192-255

    .. autoclass:: VarintEventBase
    .. autoclass:: StrEventBase
    .. autoclass:: AsciiEvent
    .. autoclass:: UnicodeEvent
    .. autoclass:: DataEventBase
    .. autoclass:: UnknownDataEvent
    .. autoclass:: StructEventBase
    .. autoclass:: ListEventBase

EventTree
^^^^^^^^^

.. autoclass:: EventTree
   :members:

Models
------

.. automodule:: pyflp._models

Implementing a model
^^^^^^^^^^^^^^^^^^^^

A look at the **source code** will definitely help, although these are a few
points that must be kept in mind when Implementing a model:

1. Does the model mimic the hierarchy exposed by FL Studio's GUI?

   .. tip::

      Browse through the hierarchies of :class:`pyflp.channel.Channel`
      subclasses to get a very good idea of this.

2. Are ``__dunder__`` methods provided by Python used whenever possible?
3. Is either :class:`ModelReprMixin` subclassed or ``__repr__`` implemented?

Descriptors
-----------

.. automodule:: pyflp._descriptors
