🚫 Limitations
===============

Before you begin reading, I would like to **emphasize** that FLP is a closed
and undocumented format. The knowledge needed for understanding the internals
is published nowhere, except for a few notes lying around here and there and
some existing implementations which I deeply thank for saving my time.

Whatever PyFLP does, is on a best-effort level. Things can go wrong so its
always wise to have **backups** and *avoid* **overwriting**.

Most properties are discovered; their representations aren't
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will find almost all the properties you could imagine. However FLP being
a binary format stores any and all kinds of stuff as integers. Its actually
harder to calculate the formula used for representing stuff like frequency,
volume and other such non-linear stuff.

Another thing is musical timings, check :github:issue:`75` for a more info.

Items cannot be added or removed, only modified
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I am working on making it possible to add or remove items (like channels,
patterns, MIDI notes, arrangements etc.) currently.

Certain things like MIDI notes are simpler to add, but things like patterns
and channels will be harder to get correct at. For those things, a **clone**
like operation is easier to implement.

.. note::

   It is possible, however (as of PyFLP 2.0.0a4) to add or remove events.
   If you don't know what they are, you probably shouldn't be handling them.
   If you are confident about working with events directly, you can very
   much add new events to effectively do things like adding your own items.

Why is it *slow*?
^^^^^^^^^^^^^^^^^

Slow is a relative term - to some it might not be noticeable at all.
Although in my opinion, PyFLP has become way slower since I migrated to
``construct``, which provides a lot more benefits than what I did earlier.

``construct`` has an opt-in compilation feature which although isn't usable
for all kinds of structs, is available for most of them, which gived quite a
speed boost for structs that occur a lot (MIDI notes, playlist items to name
a few.)

* Due to PyFLP's lazily evaluated nature, most delays don't occur upfront i.e
  during :meth:`pyflp.parse`.
* Python enums are quite slow, to the point that adding the ``f-enum`` library
  patch, reduced parse time by 50%.
* :class:`pyflp._events.EventTree` class' need for ``sortedcontainers.SortedList``
  which is implemented in pure Python.

I am all ears if anyone has any suggestions on improving PyFLP's performance.
