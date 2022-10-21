❓ FAQ
======

Now I don't frequently get asked any questions, *(I would love to)* but these
are some questions I think a newcomer or a contributor might ask?

🗣 How do I get help?
^^^^^^^^^^^^^^^^^^^^^

- Check the [discussions](https://github.com/demberto/PyFLP/discussions), open
  a new one.
- Open an issue if you spot a bug 🐛 or want a new feature ✨.
- Email me on demberto(at)proton.me.

I will generally get back to you within a day ⏰.

✨ Is "X" supported / implemented?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pretty much. I have organised PyFLP's code to be pretty self explanatory.
If you are completely new to the terminology used by PyFLP, you should also
open up FL Studio's documentation open besides the `reference <./reference>`_.

If you find something isn't yet implemented, open an issue or, a
:doc:`PR <./contributing>` if you have implemented something.

➕➖ Why is there no functionality to **add** / **remove** items from collections?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Also answers alternative specific questions like "Why can't I add a channel to
the channel rack?", "Why can't I add a new arrangement?"*

**Because of version compatibility**. The FLP format is a closed-source format
with no documentation. It evolves completely at the whims of Image-Line. I don't
work there, nor have a contributor who knows for sure that a particular thing I
implement will work for sure. *So*, instead of developing a feature which isn't
guaranteed to work, I can better devote my time to support the **modification**
of existing properties and items.

However, some good news now. I am planning to add support for adding / removing
notes from a pattern, adding / deleting automation points. Basically stuff,
which hasn't changed a lot since FL Studio first introduced it.

🤝 I want to contribute
^^^^^^^^^^^^^^^^^^^^^^^^

Please check the :doc:`contributor's guide <./contributing>` if you are new to
PyFLP. Check the :doc:`architecture` to understand the internals.

Also check out the :doc:`developer guides <./guides>`.

🧵 Is PyFLP thread safe?
^^^^^^^^^^^^^^^^^^^^^^^^^

**No.** PyFLP uses ``sortedcontainers``, an awesome library which unfortunately
`isn't thread-safe <https://github.com/grantjenks/python-sortedcontainers/issues/105>`_.
