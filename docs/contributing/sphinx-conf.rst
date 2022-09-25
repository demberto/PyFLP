🛠 Sphinx configuration
=======================

Sphinx is the tool I use for generating PyFLP's docs. It comes with a handy
plugin called ``sphinx-autodoc`` to automatically generate documentation for
the code from Python docstrings.

One thing about it, however is that its primarily reStructuredText driven,
while my docstrings are all in Github-flavored markdown. Luckily, Sphinx being
powerful and extensible provides APIs to modify the docstrings that are sent to
the ``sphinx-autodoc`` plugin.

Currently, the transformation is divided into these steps (in order):

- ⤵ Replacing ``*New in FL Studio ...*`` with shields like these:

  .. image:: https://img.shields.io/badge/FL%20Studio-20+-5f686d?labelColor=ff7629&style=for-the-badge

- ➕ Adding the correct annotations for the `descriptors <./about-descriptors>`.
- ⤵ Converting GFM tables and images in the docstrings to reStructuredText.
- ➖ Removing erroneous ``__init__`` method signatures from enums and models.
- ➕ Include "private" (obsolete) :class:`pyflp._events.EventEnum` members.
- ➕ Include model dunder methods like ``__len__``, ``__iter__`` etc.

Check `conf.py <https://github.com/demberto/PyFLP/blob/master/docs/conf.py>`_
for understanding how it is done.
