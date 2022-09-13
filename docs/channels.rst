Channel Rack
=============

.. module:: pyflp.channel
.. image:: img/channel/rack.png
.. autoclass:: ChannelRack
   :members:

Channel Types
-------------

.. autoclass:: Channel
   :members:

.. image:: img/channel/automation.png
.. autoclass:: Automation
   :members:

.. autoclass:: Instrument
   :members:

.. image:: img/channel/layer.png
.. autoclass:: Layer
   :members:

.. image:: img/channel/sampler.png
.. autoclass:: Sampler
   :members:

.. autoclass:: DisplayGroup
   :members:

Classes
-------

These implement functionality used by :class:`Channel` or its subclasses.

.. image:: img/channel/arp.png
.. autoclass:: Arp
   :members:

.. image:: img/channel/delay.png
.. autoclass:: Delay
   :members:

.. image:: img/channel/envelope.png
.. autoclass:: Envelope
   :members:

.. tab-set::

   .. tab-item:: Page 1

      .. image:: img/channel/fx1.png

   .. tab-item:: Page 2

      .. image:: img/channel/fx2.png

.. autoclass:: FX
   :members:

.. image:: img/channel/keyboard.png
.. autoclass:: Keyboard
   :members:

.. image:: img/channel/level-adjusts.png
.. autoclass:: LevelAdjusts
   :members:

.. image:: img/channel/lfo.png
.. autoclass:: LFO
   :members:

.. image:: img/channel/polyphony.png
.. autoclass:: Polyphony
   :members:

.. image:: img/channel/playback.png
.. autoclass:: Playback
   :members:

.. image:: img/channel/fx/reverb.png
.. autoclass:: Reverb
   :members:

.. image:: img/channel/time.png
.. autoclass:: Time
   :members:

.. image:: img/channel/stretching.png
.. autoclass:: TimeStretching
   :members:

.. image:: img/channel/tracking.png
.. autoclass:: Tracking
   :members:

Enumerations
------------

.. autosummary::
   :nosignatures:

   ArpDirection
   ChannelType
   LFOShape
   ReverbType

.. autoclass:: ArpDirection
   :members:
.. autoclass:: ChannelType
   :members:
.. autoclass:: LFOShape
   :members:
.. autoclass:: ReverbType
   :members:

Event IDs
---------

.. autoclass:: ChannelID
   :members:
   :member-order: bysource
.. autoclass:: DisplayGroupID
   :members:
   :member-order: bysource
.. autoclass:: RackID
   :members:
   :member-order: bysource

Exceptions
----------

.. autoexception:: ChannelNotFound
