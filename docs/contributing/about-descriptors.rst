Descriptors
===========

.. automodule:: pyflp._descriptors
   :show-inheritance:

Descriptors are one of the main reasons why PyFLP has been possible with very
little code duplication while providing a clean Pythonic interface. You can
read more about them here:

- <https://docs.python.org/3/howto/descriptor.html>
- <https://realpython.com/python-descriptors/>, **especially** the `Why use
  <https://realpython.com/python-descriptors/#why-use-python-descriptors>`_
  section.

❗ PyFLP 1.x *used* descriptors, but unfortunately not with lazy evaluation.
That was a major PITA. Its one of the reasons why I rewrote PyFLP in v2.0.

Reference
---------

1️⃣ Protocols
^^^^^^^^^^^^^

🙄 Since the ``typing`` module doesn't provide any type for descriptors, I
needed to create my own:

.. card:: ROProperty

   .. autoprotocol:: ROProperty

.. card:: RWProperty

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

➕ Making a new descriptor
---------------------------

.. autoclass:: PropBase
