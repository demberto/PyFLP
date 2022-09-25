Events
======

.. automodule:: pyflp._events
   :show-inheritance:

The FLP format uses a :wikipedia:`Type-length-value` implementation.
It's an incredibly bad format, full of bad design decisions *AFAIK*.

That being said, all the data except:

- PPQ - :attr:`pyflp.project.Project.ppq`
- Number of channels - :attr:`pyflp.project.Project.channel_count`
- Internal file format - :attr:`pyflp.project.Project.format`

is stored in a structure called an **Event**.

.. note:: C terminology

   I use some C terminology below like ``struct`` and its data types.
   I recommend you to get acquainted with these topics, however as a
   contributor, I am sure you have an equivalent programming background.

What is an **Event**?
---------------------

Following can be considered as a pseudo C-style structure of an event:

.. code-block:: c

   typedef struct {
       uint8_t id;
       void* data;
   } event;

It means that every event begins with an ID (known as the event ID) followed by
its data. The size of this ``data`` is fixed or variable sized depending on
``id``.

This table shows how the size of ``data`` is decided:

+----------+------------------------------+-------------------------------+
| Event ID | Size of ``data`` (in bytes)  | Total event size (in bytes)   |
+==========+==============================+===============================+
| 0-63     | 1                            | 1 + 1 = **2**                 |
+----------+------------------------------+-------------------------------+
| 64-127   | 2                            | 1 + 2 = **3**                 |
+----------+------------------------------+-------------------------------+
| 128-191  | 4                            | 1 + 4 = **5**                 |
+----------+------------------------------+-------------------------------+
| 192-255  | ``varint``                   | 1 + ``encoded`` + ``decoded`` |
+----------+------------------------------+-------------------------------+

Representation
--------------

An event ID is represented in an ``EventEnum`` subclass.

.. autoclass:: EventEnumMeta
.. autoclass:: EventEnum

These enums are documented throughout the `reference <../reference>`_.

For each of the range above, I have created a number of classes to match the
exact type of ``data`` indicated by its usage. What I mean by this statement
is, multiple types with different value ranges exist for a single ID range.

    For example,

    - 4 bytes can represent :wikipedia:`Single-precision_floating-point_format`
      or an :wikipedia:`Integer_(computer_science)` or even a tuple of two
      2-byte integers.
    - 1 byte can represent a number from -128 to 127 or a number from 0 to 255,
      a boolean or event an :wikipedia:`ASCII` character.

    *.. and so on*

.. autoclass:: EventBase
   :private-members:
   :special-members:

Below are the list of classes PyFLP has, grouped according the ID range.

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
    .. autoclass:: U64DataEvent
    .. autoclass:: StrEventBase
    .. autoclass:: AsciiEvent
    .. autoclass:: UnicodeEvent
    .. autoclass:: DataEventBase
    .. autoclass:: UnknownDataEvent
    .. autoclass:: StructEventBase
    .. autoclass:: ListEventBase

Parsing
-------

Let's understand two terms first:

- Fixed size events: Events with an ``id`` between 0 to 191, basically those
  whose size is only decided by the ``id``.
- Variable size events: Events with an ``id`` between 192 to 255. The ``data``,
  its size and the existance of these events itself is decided by a number of
  factors, including but not limited to the FL Studio version used to save the
  project file in which these events are saved

Fixed size events are pretty much easy to understand, just by looking at the
code, so they won't be covered in much depth. They exist for simple things.

Variable size events store their size encoded in a "varint", followed by the
actual data whose size is equal to the contents of the decoded "varint". This
is used for strings and custom structures.

Custom structures are very similar to a collection of events collected in a
single C-style ``struct``. Why so? Event IDs are stored in a single byte,
which means a maximum of 256 IDs can be used in addition to the constraints
applied by the ID range itself.

    Image-Line, as shortsighted 🔭 it was initially, didn't probably realise
    that they will run out of the available space of 255 events pretty soon.
    There however has an alternative 💡, which wouldn't cause a major breaking
    change to the format itself.

    Now I don't work for Image-Line, but they probably thought 🤔:

        We already use variable size events for strings. We can use them for
        saving this valuable event ID space as well ❕

Fast forward many versions later, FL still uses this weird mixture of fixed and
variable size events to represent what I call a `model <./about-model>`_.

.. todo::

   Explain different types of "custom structures" (:class:`DataEventBase`
   subclasses).
