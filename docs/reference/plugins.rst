\ :material-sharp:`extension;1.2em;sd-pb-1` Plugins
===================================================

.. module:: pyflp.plugin
.. autoclass:: _PluginBase
   :members:
.. autoclass:: PluginIOInfo
   :members:

Generators
----------

.. autoclass:: BooBass
   :members:

Effects
-------

.. autoclass:: FruityBalance
   :members:
.. autoclass:: FruityCenter
   :members:
.. autoclass:: FruityFastDist
   :members:
.. autoclass:: FruityNotebook2
   :members:
.. autoclass:: FruitySend
   :members:
.. autoclass:: FruitySoftClipper
   :members:
.. autoclass:: FruityStereoEnhancer
   :members:
.. autoclass:: Soundgoodizer
   :members:

VST
---

.. autoclass:: VSTPlugin
   :members:

   .. tab-set::

      .. tab-item:: Settings

         .. image:: /img/plugin/wrapper/settings.png

         .. autoclass:: pyflp.plugin::VSTPlugin._AutomationOptions
            :members:
         .. autoclass:: pyflp.plugin::VSTPlugin._MIDIOptions
            :members:
         .. autoclass:: pyflp.plugin::VSTPlugin._UIOptions
            :members:

      .. tab-item:: Processing

         .. image:: /img/plugin/wrapper/processing.png

         .. autoclass:: pyflp.plugin::VSTPlugin._ProcessingOptions
            :members:

      .. tab-item:: Troubleshooting

         .. image:: /img/plugin/wrapper/troubleshooting.png

         .. autoclass:: pyflp.plugin::VSTPlugin._CompatibilityOptions
            :members:


Enums
-----

.. autoclass:: WrapperPage
   :members:

Event IDs
---------

.. autoclass:: PluginID
   :members:
   :member-order: bysource
