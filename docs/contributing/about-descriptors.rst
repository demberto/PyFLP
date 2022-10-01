\ :fas:`bars-staggered` Understanding descriptors
==================================================

.. automodule:: pyflp._descriptors
   :show-inheritance:

A "descriptor" provides low-level managed attribute access, according to Python
docs. *(slightly rephrased for my convenience)*. Its what ``@property`` uses
internally.

    Descriptors are one of the main reasons why PyFLP has been possible with
    very little code duplication while providing a clean Pythonic interface.

    .. note:: More about descriptors in Python

        - `<https://docs.python.org/3/howto/descriptor.html>`_
        - `<https://realpython.com/python-descriptors/>`_, **especially** the
          `Why use Python descriptors?
          <https://realpython.com/python-descriptors/#why-use-python-descriptors>`_
          section.

In PyFLP, descriptors are used to describe an attribute of a :doc:`model <./about-models>`.
Internally, they access the value of an :doc:`event <./about-events>` or one if its
keys.

Some common descriptors like ``name`` 🔤, ``color`` 🎨 or ``icon`` 🖼 are used by
multiple different types of models. The descriptors used for these can be
different depending upon the internal representation inside :doc:`events <./about-events>`.

.. note::

   Throughout the documentation, I have used the term **descriptors** and
   **properties** interchangeably.

Reference
---------

1️⃣ Protocols
^^^^^^^^^^^^^

🙄 Since the ``typing`` module doesn't provide any type for descriptors, I
needed to create my own:

.. autoprotocol:: ROProperty
.. autoprotocol:: RWProperty

2️⃣ Descriptors
^^^^^^^^^^^^^^^

.. autoclass:: StructProp
.. autoclass:: EventProp
.. autoclass:: FlagProp
.. autoclass:: NestedProp
.. autoclass:: KWProp

3️⃣ Helpers
^^^^^^^^^^^

.. autoclass:: NamedPropMixin

➕ Implementing a descriptor
-----------------------------

.. autoclass:: PropBase
