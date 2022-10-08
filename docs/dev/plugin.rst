🚶‍♂️ Walkthrough: Implementing a plugin data parser
==================================================

Implementing a native plugin data parser can be easy. Below is a walkthrough
for implementing a simple effect, :class:`Fruity Balance <pyflp.plugin.FruityBalance>`.

.. note:: Prequisites

   The steps ahead assume that you have an understanding of how binary data
   types (C's integral types, in this context) work along with a basic
   understanding of Python itself.

1. Note the parameters exposed by the plugin

.. image:: /img/dev/plugin/1-parameters.png
   :align: center
   :alt: Fruity Balance paramerers

Also take note of the **order** in which they occur. Here its **Balance**
followed by **Volume**.

2. Prepare a test FLP

Create an empty new FLP, add a **Fruity Balance** to one of the insert slots.

.. image:: /img/dev/plugin/2-load-plugin.png
   :align: center
   :alt: Fruity Balance in an insert slot

Save this FLP as ``fruity-balance.flp``.

3. Getting the plugin data

Since this is an **empty** FLP, with no other plugins loaded, you can simply
access the plugin data by,

.. code-block:: python

   import pyflp
   from pyflp.plugin import PluginID

   # Parse the FLP file into a project
   project = pyflp.parse("fruity-balance.flp")

   # Collect all the events as a dict of ID to event
   events = project.events_asdict()

   # Get the first plugin data event - the Fruity Balance one itself
   plugin_data_event = events[PluginID.Data][0]

   # Get the raw data and convert it to a tuple of 8-bit unsigned integers
   data = tuple(bytearray(plugin_data_event._struct))
   print(data)

4. Observe and analyze the output

▶ You will get an output like this:

.. code-block:: python

   (0, 0, 0, 0, 256, 0, 0, 0)

That's a total of **8 bytes** worth of data for **2 knobs**.

FL Studio *generally* uses 4 bytes for most type of data, so let's assume each
knob takes **4 bytes**.

Now compare it with the **positions** of the knobs in Fruity Balance.

.. image:: /img/dev/plugin/3-observe-knob-positions.png
   :align: center
   :alt: Observe knob positions

‼ Suddenly the data above makes sense.

How? Let me explain.

- **Balance** knob is at 12 o' clock
- **Volume** knob is somewhere at 80% of its maximum.

Now convert the 8-bit integer tuple into a two 32-bit integer tuple. We get the
values ``0`` and ``256`` respectively. So, now we know, that **Balance** is 0
(because its centred) and **Volume** is at 256. Also, since we didn't modify
them at all, these are the **default** values.

🥳 Success! We cracked it!

5. Exercise: Find out the minimum and maximums (optional, but recommended)

By rotating the knobs to their extremes and following steps 3-4 again, you can
find out the minimum and maximums of each knob.

.. hint::

   One very important place for finding out the extremes is the hint panel.

   .. image:: /img/dev/plugin/4-hint-panel.png
      :align: center
      :alt: FL Studio hint panel

6. Writing the plugin code

.. todo:: Explain properly

Have a look at the existing implementation:

.. raw:: html

   <script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fdemberto%2FPyFLP%2Fblob%2F77ddbf8d7f8bbddf864d0031015ddeafea3df593%2Fpyflp%2Fplugin.py%23L66-L67&style=github-dark-dimmed&type=code&showBorder=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>
   <script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fdemberto%2FPyFLP%2Fblob%2F77ddbf8d7f8bbddf864d0031015ddeafea3df593%2Fpyflp%2Fplugin.py%23L112-L113&style=github-dark-dimmed&type=code&showBorder=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>
   <script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fdemberto%2FPyFLP%2Fblob%2F77ddbf8d7f8bbddf864d0031015ddeafea3df593%2Fpyflp%2Fmixer.py%23L383-L395&style=github-dark-dimmed&type=code&showBorder=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>
   <script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fdemberto%2FPyFLP%2Fblob%2F77ddbf8d7f8bbddf864d0031015ddeafea3df593%2Fpyflp%2Fplugin.py%23L428-L450&style=github-dark-dimmed&type=code&showBorder=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>
