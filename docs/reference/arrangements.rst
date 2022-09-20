Arrangements
============

.. module:: pyflp.arrangement
.. autoclass:: Arrangements
   :members:

Arrangement
-----------

.. autoclass:: Arrangement
   :members:

Playlist
--------

.. autoclass:: PlaylistItemBase
   :members:
.. autoclass:: ChannelPlaylistItem
   :members:
   :show-inheritance: PlaylistItemBase
.. autoclass:: PatternPlaylistItem
   :members:
   :show-inheritance: PlaylistItemBase

TimeMarker
----------

.. autoclass:: TimeMarker
   :members:

.. grid::

   .. grid-item::

      .. autoclass:: TimeMarkerType
         :members:

   .. grid-item::
      :child-align: center
      :columns: auto

      .. image:: /img/arrangement/timemarker/action.png

Track
-----

.. autoclass:: Track

   .. image:: /img/arrangement/track/preview.png
      :scale: 50 %

   .. grid::
      :padding: 2 2 3 3

      .. grid-item::

         Performance options:

         * :attr:`motion`
         * :attr:`position_sync`
         * :attr:`press`
         * :attr:`tolerant`
         * :attr:`trigger_sync`
         * :attr:`queued`.

      .. grid-item::

         .. image:: /img/arrangement/track/performance-settings.png
            :align: left

   .. autoattribute:: position_sync
   .. autoattribute:: press
   .. autoattribute:: tolerant
   .. autoattribute:: trigger_sync
   .. autoattribute:: queued
   .. autoattribute:: color

.. grid::

   .. grid-item::

      .. autoclass:: TrackMotion
         :members:

   .. grid-item::
      :child-align: center
      :columns: auto

      .. image:: /img/arrangement/track/motion.png

.. grid::

   .. grid-item::

      .. autoclass:: TrackPress
         :members:

   .. grid-item::
      :child-align: center
      :columns: auto

      .. image:: /img/arrangement/track/press.png

.. grid::

   .. grid-item::

      .. autoclass:: TrackSync
         :members:

   .. grid-item::
      :child-align: center
      :columns: auto

      .. image:: /img/arrangement/track/sync.png

Classes
-------

.. grid::

   .. grid-item::

      .. autoclass:: TimeSignature
         :members:

   .. grid-item::
      :child-align: center
      :columns: auto

      .. image:: /img/arrangement/time-signature.png


Event IDs
---------

.. autoclass:: ArrangementsID
   :members:
   :member-order: bysource
.. autoclass:: ArrangementID
   :members:
   :member-order: bysource
.. autoclass:: TimeMarkerID
   :members:
   :member-order: bysource
.. autoclass:: TrackID
   :members:
   :member-order: bysource
