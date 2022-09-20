PyFLP
=====

PyFLP is a parser for FL Studio project files written in Python.

.. raw:: html

    <table>
      <colgroup>
        <col style="width: 10%;"/>
        <col style="width: 90%;"/>
      </colgroup>
      <tbody>
        <tr>
          <th>CI</th>
          <td>
            <img alt="build" src="https://img.shields.io/github/workflow/status/demberto/pyflp/main"/>
            <a href="https://pyflp.readthedocs.io/en/latest/">
              <img alt="Documentation Build Status" src="https://img.shields.io/readthedocs/pyflp/latest?logo=read-the-docs"/>
            </a>
            <a href="https://results.pre-commit.ci/latest/github/demberto/PyFLP/master">
              <img alt="pre-commit-ci" src="https://results.pre-commit.ci/badge/github/demberto/PyFLP/master.svg"/>
            </a>
          </td>
        </tr>
        <tr>
          <th>PyPI</th>
          <td>
            <a href="https://pypi.org/project/PyFLP">
              <img alt="PyPI - Package Version" src="https://img.shields.io/pypi/v/PyFLP"/>
            </a>
            <a href="https://pypi.org/project/PyFLP">
              <img alt="PyPI - Supported Python Versions" src="https://img.shields.io/pypi/pyversions/PyFLP?logo=python&amp;logoColor=white"/>
            </a>
            <a href="https://pypi.org/project/PyFLP">
              <img alt="PyPI - Supported Implementations" src="https://img.shields.io/pypi/implementation/PyFLP"/>
            </a>
            <a href="https://pypi.org/project/PyFLP">
              <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/PyFLP"/>
            </a>
          </td>
        </tr>
        <tr>
          <th>Activity</th>
          <td>
            <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2022"/>
            <a href="https://pypistats.org/packages/pyflp">
              <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/PyFLP"/>
            </a>
          </td>
        </tr>
        <tr>
          <th>QA</th>
          <td>
            <a href="https://codecov.io/gh/demberto/PyFLP">
              <img alt="codecov" src="https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF"/>
            </a>
            <a href="https://codefactor.io/repository/github/demberto/PyFLP">
              <img alt="CodeFactor Grade" src="https://img.shields.io/codefactor/grade/github/demberto/PyFLP?logo=codefactor"/>
            </a>
            <a href="https://github.com/pre-commit/pre-commit">
              <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&amp;logoColor=white"/>
            </a>
            <a href="https://github.com/PyCQA/bandit">
              <img alt="Security Status" src="https://img.shields.io/badge/security-bandit-yellow.svg"/>
            </a>
          </td>
        </tr>
        <tr>
          <th>Other</th>
          <td>
            <a href="https://github.com/demberto/PyFLP/blob/master/LICENSE">
              <img alt="License" src="https://img.shields.io/github/license/demberto/PyFLP"/>
            </a>
            <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/demberto/PyFLP"/>
            <a href="https://github.com/psf/black">
              <img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-black"/>
            </a>
            <a href="https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md">
              <img alt="covenant" src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg"/>
            </a>
          </td>
        </tr>
      </tbody>
    </table>

Installation
------------

PyFLP requires **Python 3.7+**.

.. tab-set::

    .. tab-item:: PyPi (Recommended)

      In a terminal, enter

      .. code-block::

          python -m pip install -U pyflp

    .. tab-item:: Github repo

      1. Clone this repo

      .. code-block::

          git clone https://github.com/demberto/PyFLP

      1. Navigate to newly created folder

      .. code-block:: bat

          cd PyFLP

      1. Install

        Normal installation:

        .. code-block::

            pip install .

        *This allows you to install a version with the latest changes from the
        repo. However, it might be broken.*

        *OR*

        Editable install:

        .. code-block::

            pip install -e .

        *Preferred way for developing and testing PyFLP, if virtualenv is not
        an option for you.*

    .. tab-item:: Github releases

        1. Go to `Releases <https://github.com/demberto/PyFLP/releases>`_ tab.

        2. Download the build distrbution wheel (\ **.whl**\) and the
            source tarball (\ **.tar.gz**\ ), optionally.

        3. Install them via pip, for e.g.

            .. code-block::

              pip install pyflp-2.0.0-py3-none-any.whl

Getting Started
---------------

Load a project file:

.. code-block:: python

    import pyflp
    project = pyflp.parse("/path/to/parse.flp")

Save the project:

.. code-block:: python

    pyflp.save(project, "/path/to/save.flp")

Check the user guide for more information.

Navigation
----------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   user-guide
   reference
   contributing
   changelog

.. sidebar-links::
   :github:
   :pypi: PyFLP

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
