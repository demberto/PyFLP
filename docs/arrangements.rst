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

.. grid:: auto

   .. grid-item::

      .. autoclass:: TimeMarkerType
         :members:

   .. grid-item::
      :child-align: center

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

.. grid:: auto

   .. grid-item::

      .. autoclass:: TrackMotion
         :members:

   .. grid-item::
      :child-align: center

      .. image:: /img/arrangement/track/motion.png

.. grid:: auto

   .. grid-item::

      .. autoclass:: TrackPress
         :members:

   .. grid-item::
      :child-align: center

      .. image:: /img/arrangement/track/press.png

.. grid:: auto

   .. grid-item::

      .. autoclass:: TrackSync
         :members:

   .. grid-item::
      :child-align: center

      .. image:: /img/arrangement/track/sync.png

Classes
-------

.. grid:: auto

   .. grid-item::

      .. autoclass:: TimeSignature
         :members:

   .. grid-item::
      :child-align: center

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
