\ :fas:`ellipsis` Events
========================

    This section is intended for those who want to delve into PyFLP's low-level
    API or understand how internally events are ordered. A good understanding
    of FL Studio's GUI is assumed.

When to use the low level API?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If PyFLP fails to parse a particular model or you want to dive deep into the
true / raw / real (whatever you want to call it) representation of an FLP.

.. seealso:: :ref:`Binary layout <architecture-event>` of an event

Structure
---------

    Very early versions of FL Studio were literally a **dump** of the changes
    taking place in FL's GUI. Say for example, you create a channel and *then*
    add notes to some pattern; the events for those would be dumped in the same
    order.

    Hopefully its not the same now, but some of those characteristics are still
    visible.

.. caution::

    DO NOT use the following section as a definitive / complete source of
    information for adding / removing your own events. While *most likely* your
    events will get parsed correctly, there's always a chance of corrupting
    your FLPs.

This is *roughly* the order of the events (as of latest FL Studio):

1. Project-wide / metadata
2. Display groups / channel filters
3. Initialised controls
4. Pattern notes / controllers
5. MIDI remote controllers
6. Internal remote controllers / automations
7. 1st channel
8. Pattern metadata
9. Remaining channels
10. Arrangements:

    a. Index, name
    b. Playlist items
    c. Time markers
    d. Tracks:

        I. All data except name
        II. Name

11. Mixer:

    a. Inserts:

        A list of events in the order:

        I. Color, name, icon and flags
        II. Effect slots
        III. Post EQ, input/output, routing

    b. Remaining insert data
12. Channel rack height

Channel
^^^^^^^

There are currently 5 types of channels (specified in :class:`ChannelType`).
Although some of them don't use certain events, FL Studio dumps the same
event tree for any type of channel. For e.g. a :class:`Layer` channel will have
all the events a :class:`Sampler` channel has, irrespective of whether the
events have any meaning in that context. Certain channels have extra events.

=== =================================== ================================================
#   Event ID                            Model / property
=== =================================== ================================================
1   :attr:`ChannelID.New`               :attr:`Channel.iid`
2   :attr:`ChannelID.Type`              :class:`Channel` subclasses
3   :attr:`PluginID.InternalName`       :attr:`Channel.internal_name`
4   :attr:`PluginID.Wrapper`            :attr:`Instrument.plugin`
5   :attr:`PluginID.Name`               :attr:`Channel.name`
6   :attr:`PluginID.Icon`               :attr:`Channel.icon`
7   :attr:`PluginID.Color`              :attr:`Channel.color`
8   :attr:`PluginID.Data`               :attr:`Instrument.plugin`
9   :attr:`ChannelID.IsEnabled`         :attr:`Channel.enabled`
10  :attr:`ChannelID.Delay`             :attr:`_SamplerInstrument.delay` [#1]_
11  :attr:`ChannelID.DelayModXY`        :attr:`_SamplerInstrument.delay` [#1]_
12  :attr:`ChannelID.Reverb`            :attr:`Sampler.fx.reverb`
13  :attr:`ChannelID.TimeShift`         :attr:`_SamplerInstrument.time.shift` [#1]
14  :attr:`ChannelID.Swing`             :attr:`_SamplerInstrument.time.swing` [#1]_
15  :attr:`ChannelID.FreqTilt`          :attr:`Sampler.fx.freq_tilt`
16  :attr:`ChannelID.Pogo`              :attr:`Sampler.fx.pogo`
17  :attr:`ChannelID.Cutoff`            :attr:`Sampler.fx.cutoff`
18  :attr:`ChannelID.Resonance`         :attr:`Sampler.fx.reso`
19  :attr:`ChannelID.Preamp`            :attr:`Sampler.fx.boost`
20  :attr:`ChannelID.FadeOut`           :attr:`Sampler.fx.fade_out`
21  :attr:`ChannelID.FadeIn`            :attr:`Sampler.fx.fade_in`
22  :attr:`ChannelID.StereoDelay`       :attr:`Sampler.fx.stereo_delay`
23  :attr:`ChannelID.RingMod`           :attr:`Sampler.fx.ringmod`
24  :attr:`ChannelID.FXFlags`           Quite a few, refer code.
25  :attr:`ChannelID.RoutedTo`          :attr:`_SamplerInstrument.insert` [#1]_
26  :attr:`ChannelID.Levels`            :attr:`Sampler.filter` + few more
27  :attr:`ChannelID.LevelAdjusts`      :attr:`_SamplerInstrument.level_adjusts` [#1]_
28  :attr:`ChannelID.Polyphony`         :attr:`_SamplerInstrument.polyphony` [#1]_
29  :attr:`ChannelID.Parameters`        A lot; spread across many models.
30  :attr:`ChannelID.CutGroup`          :attr:`_SamplerInstrument.cut_group` [#1]_
31  :attr:`ChannelID.LayerFlags`        :attr:`Layer.random`, :attr:`Layer.crossfade`
32  :attr:`ChannelID.GroupNum`          :attr:`Channel.group`
33* :attr:`ChannelID.Automation`        :class:`Automation`
34  :attr:`ChannelID.IsLocked`          :attr:`Channel.locked`
35  :attr:`ChannelID.Tracking` * 2      :attr:`_SamplerInstrument.tracking` [#1]_
37  :attr:`ChannelID.EnvelopeLFO` * 5   :attr:`Sampler.envelopes`, :attr:`Sampler.lfos`
42  :attr:`ChannelID.SamplerFlags`      Certain :class:`Sampler` properties.
43  :attr:`ChannelID.PingPongLoop`      :attr:`Sampler.playback.ping_pong_loop`
44* :attr:`ChannelID.SamplePath`        :attr:`Sampler.sample_path` [#2]_
=== =================================== ================================================

.. [#1] :class:`Sampler` & :class:`Instrument` base off of :class:`_SamplerInstrument`.
.. [#2] Optional event for :class:`Sampler` only.

Pattern
^^^^^^^

:class:`Pattern` events are serialised at 2 different places inside an FLP.
The first section contains the notes and controllers held by a pattern if any.

= ============================= ===========================
# Event ID                      Property
= ============================= ===========================
1 :attr:`PatternID.New`         :attr:`Pattern.iid`
2 :attr:`PatternID.Controllers` :attr:`Pattern.controllers`
3 :attr:`PatternID.Notes`       :attr:`Pattern.notes`
= ============================= ===========================

The next section contains colour, icon, timemarkers and any new events get
added here. Some events aren't listed because their order is not confirmed yet.

= ============================= ======================
# Event ID                      Property
= ============================= ======================
1 :attr:`PatternID.New` [#3]_   :attr:`Pattern.iid`
2 :attr:`PatternID.Name`        :attr:`Pattern.name`
3 :attr:`PatternID.Color`       :attr:`Pattern.color`
4 157 [#3]_                     N.A.
5 158 [#3]_                     N.A
6 164 [#3]_                     N.A.
= ============================= ======================

.. [#3] Acts as an identifier here.
.. [#4] Unknown events; complete list `here <https://github.com/demberto/PyFLP/discussions/34>`_.

VST plugin parsing
^^^^^^^^^^^^^^^^^^

Implemented in :class:`VSTPluginEvent`, this is arguably the hardest event to
parse *cleanly*. If you are familiar with PyFLP's internals, you might be
surprised to know that this event has events *inside events*. Why a struct
wasn't usable is beyond me.
