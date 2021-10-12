# Entry-point classes

## [**Parser**](reference/parser.md)

Most of the times this is only what you will actually need.

## [**Project**](reference/project.md)

`Parser` will create this _whenever it can_.

---

# [Event](reference/event/event.md)

### [ByteEvent](reference/event/byte.md)

### [WordEvent](reference/event/word.md)

### [DWordEvent](reference/event/dword.md)

### [TextEvent](reference/event/text.md)

### [DataEvent](reference/event/data.md)

---

# FLP Object Model

## [FLObject](reference/flobject.md)

Abstract base class for the FLP object model.

## [Arrangement](reference/arrangement/arrangement.md)

Contains `Playlist`, `TimeMarker` and `Track`.

### Playlist

This class has nothing special yet, just a parse method, so no docs.

### [TimeMarker](reference/arrangement/timemarker.md)

### [Track](reference/arrangement/track.md)

## [Channel](reference/channel/channel.md)

Contains `ChannelFX`, `ChannelDelay` and `FilterChannel`.

### [ChannelFX](reference/channel/fx.md)

### [ChannelDelay](reference/channel/delay.md)

::: pyflp.flobject.channel.delay.ChannelDelay
    selection:
      members:
        - __doc__

### [FilterChannel](reference/channel/filterchannel.md)

::: pyflp.flobject.FilterChannel
    selection:
      members:
        - __doc__

## [Insert](reference/insert/insert.md)

::: pyflp.flobject.Insert
    selection:
      members:
        - __doc__

### [InsertSlot](reference/insert/slot.md)

::: pyflp.flobject.InsertSlot
    selection:
      members:
        - __doc__

## [Misc](reference/misc.md)

::: pyflp.flobject.Misc
    selection:
      members:
        - __doc__

## [Pattern](reference/pattern/pattern.md)

Contains `Note`

### [(MIDI) Note](reference/pattern/note.md)

## Plugin

### [VSTPlugin](reference/plugin/vst.md)

Implementation of `InsertSlotEvent.Plugin` event for these stock FX plugins

### [Fruity Balance](reference/plugin/balance.md)

### [Fruity Notebook 2](reference/plugin/notebook2.md)

### [Fruity Soft Clipper](reference/plugin/soft_clipper.md)

### [Soundgoodizer](reference/plugin/soundgoodizer.md)

---

## [Exceptions](reference/exceptions.md)

## [Utils](reference/utils.md)
