|pytest-icon| Unit Testing
==========================

Writing sane unit tests for an undocumented binary format which we have
basically no control over 😫; for a parser made almost completely by reversing
the format is hard.

Luckily, FL Studio comes with a handy feature 🚀 to export "presets" for various
`models <./models.rst>`_ like :class:`Channel`, :class:`Insert` and so on. This
is used for **isolating** test results. A look 👀 at `tests/assets directory
<https://github.com/demberto/PyFLP/tree/master/tests/assets>`_ shows what
possible models and properties could be tested from a preset file. I have tried
to divide into a single model or an individual property whenever possible.

These presets have the same layout of a normal full FLP would use, but only the
required events are kept. This *might* and **has** caused some problems while
testing properties dependant on data passed from its parent 😔. For instance, an
:class:`Insert` gets version from :class:`Mixer` which gets it from
:class:`Project` itself. This kind of dependency is not good in my opinion 😐,
and I continue to look at ways to improve testing.

There also are models which cannot be exported into presets, notable being
:class:`Pattern` (although scores can be exported) and the entire
:mod:`pyflp.arrangement` module. Currently, I have kept the testing for these
in a common FLP.

That being said, PyFLP's unit testing has come a long way - earlier it was all
done in a single FLP. I still have to find a way to test setters properly,
since its one of PyFLP's unique features. If you have an idea 💡, I would ♥ to
hear.

.. |pytest-icon| image:: /img/contributing/pytest.svg
    :width: 32

.. todo:: Find a way to color SVGs
