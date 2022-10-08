\ :fas:`user-gear` Contributor's Guide
======================================

🤝 All contributions are welcome.

.. important::

   PyFLP adheres to the `Contributor Covenant Code of Conduct
   <https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md>`_.
   Please make sure you have read it and accept it before proceeding further.

⬇ The sections below are ordered roughly in the order one would follow.

\ :fas:`code-pull-request;sd-text-primary` Making a PR
------------------------------------------------------

.. tip:: Format code with ``black``

   PyFLP use the black code style, format your code with it.

:fas:`clone` Clone the repo
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   git clone https://github.com/demberto/PyFLP

:fas:`code-branch` Create a branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

   git branch my_new_feature
   git checkout my_new_feature

🌱 Create a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I prefer to use `venv <https://docs.python.org/3/library/venv.html>`_.

.. code-block:: console

   python -m venv venv

This will create a folder named ``venv`` in the current directory.

Now, activate the venv:

.. code-block:: console

   ./venv/Scripts/activate

📌 Install dependencies
^^^^^^^^^^^^^^^^^^^^^^^^

Install all dev, user and docs dependencies.

.. code-block:: console

   python -m pip install --upgrade pip
   pip install -r requirements.txt -r docs/requirements.txt tox

|vscode-icon| VS Code integration
---------------------------------

I use VS Code for development. I have made certain changes to the workspace to
suit my workflows and make life easier.

.. todo Inspect whether venv creation can be automated through VSCode.

:fab:`python` Python extension configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To ease linting, enforce strict type checking and improve code quality, I have
modified certain settings for the official Python / Pylance extension, so that
you don't need to manually configure it or encounter issues while committing.
Check `settings.json
<https://github.com/demberto/PyFLP/blob/master/.vscode/settings.json>`_.

:material-sharp:`extension;1.2em;sd-pb-1` Recommended extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you open the repo directory in VS Code, you will get recommendations for
extensions. I use these extensions myself. You can check `extensions.json
<https://github.com/demberto/PyFLP/blob/master/.vscode/extensions.json>`_ to
know why and where they are used.

:fas:`list-check` Tasks
^^^^^^^^^^^^^^^^^^^^^^^

If you use :fab:`windows;sd-text-secondary` Windows, I have made some shortcuts
for common tasks. Check `tasks.json
<https://github.com/demberto/PyFLP/blob/master/.vscode/tasks.json>`_.

.. |vscode-icon| image:: /img/contributing/vscode.svg
   :width: 32

|pytest-icon| Testing
---------------------

FL Studio comes with a handy feature 🚀 to export "presets" for various
:doc:`models <./architecture>` like :class:`Channel`, :class:`Insert` and so
on. This is used for **isolating** test results. A look 👀 at `tests/assets
directory <https://github.com/demberto/PyFLP/tree/master/tests/assets>`_ shows
what possible models and properties could be tested from a preset file. I have
divided the tests such that they test a model or an individual property.

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

✴️ Guidelines
^^^^^^^^^^^^^^

1. Follow the naming scheme of the test functions, it generally follows the
   format of  ``test_{model_collection}`` *or* ``test_{model}_{descriptor}``.
2. Create separate test assets, whenever possible.

.. |pytest-icon| image:: /img/contributing/pytest.svg
    :width: 32

📖 Docs
--------

Don't forget to update the `docs <https://pyflp.rtfd.io/>`_ after you are done
with a feature or a bug fix that affects the documentation.

✴️ Guidelines
^^^^^^^^^^^^^^

1. ↔ **80 columns** max, wherever possible. Don't consider this for inlined links
   and tables.

   .. tip::

      Don't start a new sentence at the end of a line. Remember that it should
      be easily readable to you, first of all.

2. 🌐 **Inline links** if they aren't used twice in the same document.
3. 📝 Should look **clean** enough in a simple text viewer as well.
4. 💡 Use **emojis** if it conveys the meaning of the text next to it.
5. ⚫⚪ Add images for both **light** and **dark** modes.

🛠 Sphinx configuration
^^^^^^^^^^^^^^^^^^^^^^^

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

- ➕ Adding the correct annotations for the :doc:`descriptors <./architecture>`.
- ⤵ Converting GFM tables and images in the docstrings to reStructuredText.
- ➖ Removing erroneous ``__init__`` method signatures from enums and models.
- ➕ Include "private" (obsolete) :class:`pyflp._events.EventEnum` members.
- ➕ Include model dunder methods like ``__len__``, ``__iter__`` etc.

Check `conf.py <https://github.com/demberto/PyFLP/blob/master/docs/conf.py>`_
for understanding how it is done.

🚧 Still to be documented
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. todolist::
