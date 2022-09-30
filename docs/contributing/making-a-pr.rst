\ :fas:`code-pull-request;sd-text-primary` Making a PR
======================================================

.. tip:: Format code with ``black``

   PyFLP use the black code style, format your code with it.

:fas:`clone` Clone the repo
---------------------------

.. code-block:: console

   git clone https://github.com/demberto/PyFLP

:fas:`code-branch` Create a branch
----------------------------------

.. code-block:: console

   git branch my_new_feature
   git checkout my_new_feature

🌱 Create a virtual environment
--------------------------------

I prefer to use `venv <https://docs.python.org/3/library/venv.html>`_.

.. code-block:: console

   python -m venv venv

This will create a folder named ``venv`` in the current directory.

Now, activate the venv:

.. code-block:: console

   ./venv/Scripts/activate

📌 Install dependencies
------------------------

Install all dev, user and docs dependencies.

.. code-block:: console

   python -m pip install --upgrade pip
   pip install -r requirements.txt -r docs/requirements.txt tox

🔬 Testing
-----------

* Check the comments inside `test FLP
  <https://github.com/demberto/PyFLP/blob/master/tests/assets/FL%2020.8.4.flp>`_.
* Create a virtual environment before setting up.

📖 Docs
--------

Don't forget to update the `docs <https://pyflp.rtfd.io/>`_ after you are done
with a feature or a bug fix that affects the documentation.
