Installation
============

.. tab-set::

    .. tab-item:: PyPi (Recommended)

      .. code-block::

        pip install --upgrade pyflp

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

              pip install pyflp-1.1.0-py3-none-any.whl
