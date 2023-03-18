\ :fas:`file-waveform` Project
==============================

.. module:: pyflp.project

.. autoclass:: Project
   :members:

   .. dropdown:: Information page
      :open:

      .. grid::

         .. grid-item::
            :columns: auto

            * :attr:`Project.artists`
            * :attr:`Project.created_on`
            * :attr:`Project.comments`
            * :attr:`Project.genre`
            * :attr:`Project.show_info`
            * :attr:`Project.url`
            * :attr:`Project.time_spent`

         .. grid-item::
            :columns: 12 8 8 8
            :margin: auto

            .. image:: /img/project/info.png

   .. dropdown:: Settings page
      :open:

      .. grid::

         .. grid-item::

            * :attr:`Project.data_path`
            * :attr:`Project.pan_law`
            * :attr:`Project.ppq`
            * :attr:`Arrangements.time_signature <pyflp.arrangement.Arrangements.time_signature>`
            * :attr:`Patterns.play_cut_notes <pyflp.pattern.Patterns.play_cut_notes>`

         .. grid-item::

            .. image:: /img/project/settings.png
               :align: right

Enums
-----

.. autoclass:: FileFormat
   :members:
   :member-order: bysource

.. autoclass:: PanLaw
   :members:
   :member-order: bysource

.. autoclass:: ProjectID
   :members:
   :member-order: bysource
