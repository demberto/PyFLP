🏠 Architecture
================

    The content below assumes you have fairly good knowledge of the following:

    - OOP and descriptors, especially
    - Type annotations
    - Binary data types and streams

.. svgbob::
   :align: center
   :fill-color: #ffff00
   :font-family: Arial
   :stroke-color: #00ffff

   +---------------+       +----------------+    +--> Descriptor 1
   | Events        |       | Models         |   /
   |               |------>|                |--+
   | Low level API |       | High level API |   \
   +---------------+       +----------------+    +--> Descriptor 2

PyFLP provides a high-level and a low-level API. Normally the high-level API
should get your work done. However, it might be possible that due to a bug or
super old versions of FLPs the high level API fails to parse. In that case,
one can use the low-level API. Using it requires a deeper understanding of
the FLP format and how the GUI hierarchies relate to their underlying events.

.. caution::

   Using the high-level and low-level API simultaneously can cause a loss of
   synchronisation across the state, although it normally shouldn't this
   use-case should be considered untested.

⬇ The sections below are ordered from low-level to high-level concepts.

.. _architecture-event:

Understanding events
--------------------

.. automodule:: pyflp._events
   :show-inheritance:

The FLP format uses a :wikipedia:`Type-length-value` encoding to store almost
all of it's data. *It's an incredibly bad format, full of bad design decisions
AFAIK.*

That being said, all the data except:

- PPQ - :attr:`pyflp.project.Project.ppq`
- Number of channels - :attr:`pyflp.project.Project.channel_count`
- Internal file format - :attr:`pyflp.project.Project.format`

is stored in a structure called an **Event**.

❔ What is an **Event**?
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: C terminology

   I use some C terminology below like ``struct`` and its data types.
   I recommend you to get acquainted with these topics, however as a
   contributor, I am sure you have an equivalent programming background.

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

Events are the first stage of parsing in PyFLP. The :meth:`pyflp.parse` method
gathers all events by reading an FLP file as a binary stream.

Representation
^^^^^^^^^^^^^^

An event ID is represented in an ``EventEnum`` subclass.

.. autoclass:: _EventEnumMeta
.. autoclass:: EventEnum

These enums are documented throughout the :doc:`reference`.

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
    .. autoclass:: StrEventBase
    .. autoclass:: AsciiEvent
    .. autoclass:: UnicodeEvent
    .. autoclass:: DataEventBase
    .. autoclass:: UnknownDataEvent
    .. autoclass:: StructEventBase
    .. autoclass:: ListEventBase

Parsing
^^^^^^^

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
variable size events to represent what I call a :ref:`model <architecture-model>`.

.. todo::

   Explain different types of "custom structures" (:class:`DataEventBase`
   subclasses).

.. _architecture-model:

📦 Understanding models
------------------------

A **model** is an entity, or an object, programmatically speaking.

    Models are **my** estimations of object hierarchies which mainly mimic FL
    Studio's GUI hierarchy. I figured out that this is the easiest way to
    expose an API programmatically.

    The FLP format has no such notion of "models" as it is entirely based on
    the sequence of :doc:`events <./architecture>`.

    PyFLP's modules are categorized to follow FL Studio' GUI hierarchy as well.
    Every module *generally* represents a **separate window** in the GUI.

In PyFLP, a model is **composed** of several :ref:`descriptors <architecture-descriptor>`,
properties and some additional helper methods, optionally. It *might* contain
additional parsing logic for nested models and collections of models.

A model's internal state is stored in :ref:`events <architecture-event>` and its
shared state is passed to it via keyword arguments. *For example*, many models
depend on :attr:`pyflp.project.Project.version` to decide the parsing logic for
certain properties. This creates a "dependancy" of the model to a "shared"
property. Such "dependencies" are passed to the model in the form of keyword
arguments and consumed by the :ref:`descriptors <architecture-descriptor>`.

A model **does NOT cache** its state in any way. This is done, mainly to:

1. Implement lazily evaluated properties and avoid use of private variables.
2. Keep the property values in sync with the event data.

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

Reference
^^^^^^^^^

.. automodule:: pyflp._models
   :show-inheritance:
   :members:

.. _architecture-descriptor:

\ :fas:`bars-staggered` Understanding descriptors
-------------------------------------------------

.. automodule:: pyflp._descriptors
   :show-inheritance:

A "descriptor" provides low-level managed attribute access, according to
Python docs. *(slightly rephrased for my convenience)*.

    IMO, it allows separation of attribute logic from the class implementation
    itself and this saves a huge amount of repretitive error-prone code.

    .. note:: More about descriptors in Python

        - `<https://docs.python.org/3/howto/descriptor.html>`_
        - `<https://realpython.com/python-descriptors/>`_, **especially** the
          `Why use Python descriptors?
          <https://realpython.com/python-descriptors/#why-use-python-descriptors>`_
          section.

In PyFLP, descriptors are used for attributes of a :ref:`model <architecture-model>`.
Internally, they access the value of an :ref:`event <architecture-event>` or
one if its keys for :class:`StructEventBase`. They can be called *stateless*
because they never cache the value which they fetch and directly dump back into
the event when their setter is invoked.

Some common descriptors like ``name`` 🔤, ``color`` 🎨 or ``icon`` 🖼 are used by
multiple different types of models. The descriptors used for these can be
different depending upon the internal representation inside :ref:`events <architecture-event>`.

Despite all this, they are normal attributes from a type-checker's POV 👁 when
accessed from an instance.

.. note::

   Throughout the documentation, I have used the term **descriptors** and
   **properties** interchangeably.

Protocols
^^^^^^^^^

🙄 Since the ``typing`` module doesn't provide any type for descriptors, I
needed to create my own:

.. autoprotocol:: ROProperty
.. autoprotocol:: RWProperty

Descriptors
^^^^^^^^^^^

.. autoclass:: PropBase
.. autoclass:: StructProp
.. autoclass:: EventProp
.. autoclass:: FlagProp
.. autoclass:: NestedProp
.. autoclass:: KWProp

Helpers
^^^^^^^

.. autoclass:: NamedPropMixin
