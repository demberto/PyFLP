\ :fas:`cubes` Understanding models
====================================

.. automodule:: pyflp._models
   :show-inheritance:

A **model** is an entity, or an object, programmatically speaking.

    Models are **my** estimations of object hierarchies which mainly mimic FL
    Studio's GUI hierarchy. I figured out that this is the easiest way to
    expose an API programmatically.

    The FLP format has no such notion of "models" as it is entirely based on
    the sequence of :doc:`events <./about-events>`.

    PyFLP's modules are categorized to follow FL Studio' GUI hierarchy as well.
    Every module *generally* represents a **separate window** in the GUI.

In PyFLP, a model is **composed** of several :doc:`descriptors <./about-descriptors>`,
properties and some additional helper methods, optionally. It *might* contain
additional parsing logic for nested models and collections of models.

A model's internal state is stored in :doc:`events <./about-events>` and its
shared state is passed to it via keyword arguments. *For example*, many models
depend on :attr:`pyflp.project.Project.version` to decide the parsing logic for
certain properties. This creates a "dependancy" of the model to a "shared"
property. Such "dependencies" are passed to the model in the form of keyword
arguments and consumed by the :doc:`descriptors <./about-descriptors>`.

A model **does NOT cache** its state in any way. This is done, mainly to:

1. Implement lazily evaluated properties and avoid use of private variables.
2. Keep the property values in sync with the event data.

Implementing a model
--------------------

A look at the **source code** will definitely help, although these are a few
points that must be kept in mind when Implementing a model:

1. Does the model mimic the hierarchy exposed by FL Studio's GUI?

   .. tip::

      Browse through the hierarchies of :class:`pyflp.channel.Channel`
      subclasses to get a very good idea of this.

2. Are ``__dunder__`` methods provided by Python used whenever possible?
3. Is either :class:`ModelReprMixin` subclassed or ``__repr__`` implemented?

Reference
---------

.. autoclass:: ModelBase
.. autoclass:: ItemModel
.. autoclass:: SingleEventModel
.. autoclass:: MultiEventModel

Helpers, Shared models
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: FLVersion
.. autoclass:: ModelReprMixin
