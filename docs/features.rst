✨ Features
============

Non-destructive editing
-----------------------

The modifications you make will have a minimum effect on the internal structure
of an FLP. Infact, I guarantee you that if you save a :class:`pyflp.Project`
as-is, the new file will be exactly alike (compare hashes if you want).

📝 Godlevel docstrings
----------------------

PyFLP has been carefully written to take advantage of the features provided
by a modern editor, like VS Code. One area, I particularly devoted a lot of
time to are docstrings.

Since PyFLP's entire documentation is only its reference, I thought it might
be challenging for a first time user to know where to find the data they need.

:fas:`eye;sd-text-info` Visual hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: /img/features/images-dark.png
   :align: center
   :class: only-dark

.. image:: /img/features/images-light.png
   :align: center
   :class: only-light

To make it somewhat easier of a journey, I haved added links to images and GIFs
from FL Studio's interface.

:fas:`table;sd-text-info` Minimums, maximums and defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: /img/features/tables-dark.png
   :align: center
   :class: only-dark

.. image:: /img/features/tables-light.png
   :align: center
   :class: only-light

A lot of properties also have *suggested* minimum, maximum and default values.
When I say suggested, I mean that FLP is a closed format owned by Image-Line.
Its on their whims what they do with it. The values I suggest are only on a
*last-I-checked-they-were-these* basis. However, my research till now has
shown me that they rarely change.

.. important:: For non-VS Code users

   VS Code uses a rather unstandardised format for parsing docstrings. Unlike
   PyCharm, it cannot parse rST docstrings. Hence PyCharm users will get a
   rather bad result from the docstring previews where I have used tables and
   images, *unfortunately*.

   I haven't found a way to make docstrings look good while being equally
   accessible in both PyCharm and VSCode.

   .. seealso:: `#52 <https://github.com/demberto/PyFLP/issues/52>`_

:octicon:`check-circle-fill;1em;sd-text-success` 100% type tested
-----------------------------------------------------------------

PyFLP is fully tested with `pyright <https://github.com/microsoft/pyright>`_,
a static type checker built right into VS Code as well as mypy.

:fas:`umbrella;sd-text-primary` 85%+ code coverage
--------------------------------------------------

PyFLP boasts a total of more than 85+ combined code coverage across supported
Python versions. Higher the coverage ⬆, lesser the amount of bugs 🐞
