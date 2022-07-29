# Plugins

PyFLP offers deserialisers for certain plugins listed below and general
information about VST plugins.

!!! info "AU plugins"

    The [VST plugin](#vst) information obtained can refer to an AU plugin as
    well. I don't have a Mac to test :(

## BooBass
[![](../img/boobass.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/BooBass.htm)
::: pyflp.models.BooBass
    options:
      filters:
        - "!DEFAULT_NAME"

## Fruity Balance
[![](../img/fruity-balance.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Balance.htm)
::: pyflp.models.FruityBalance
    options:
      filters:
        - "!DEFAULT_NAME"

## Fruity Fast Dist
[![](../img/fruity-fast-dist.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Fast%20Dist.htm)
::: pyflp.models.FruityFastDist
    options:
      filters:
        - "!DEFAULT_NAME"
::: pyflp.models.FruityFastDistKind

## Fruity Notebook 2
[![](../img/fruity-notebook2.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20NoteBook%202.htm)
::: pyflp.models.FruityNotebook2
    options:
      filters:
        - "!CODEC"
        - "!DEFAULT_NAME"

## Fruity Send
[![](../img/fruity-send.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Send.htm)
::: pyflp.models.FruitySend
    options:
      filters:
        - "!DEFAULT_NAME"

## Fruity Soft Clipper
[![](../img/fruity-soft-clipper.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Soft%20Clipper.htm)
::: pyflp.models.FruitySoftClipper
    options:
      filters:
        - "!DEFAULT_NAME"

## Fruity Stereo Enhancer
[![](../img/fruity-stereo-enhancer.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Fruity%20Stereo%20Enhancer.htm)
::: pyflp.models.FruityStereoEnhancer
    options:
      filters:
        - "!DEFAULT_NAME"

## Soundgoodizer
[![](../img/soundgoodizer.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/Soundgoodizer.htm)
::: pyflp.models.Soundgoodizer
    options:
      filters:
        - "!DEFAULT_NAME"
::: pyflp.models.SoundgoodizerMode

## VST

!!! tip "Wrapper options"

    === "Settings"

        [![](../img/wrapper-settings.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/wrapper.htm#wrapper_pluginsettings)

    === "Processing"

        [![](../img/wrapper-processing.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/wrapper.htm#wrapper_processing)

    === "Troubleshooting"

        [![](../img/wrapper-troubleshooting.png)](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/plugins/wrapper.htm#wrapper_troubleshooting)

::: pyflp.models.VSTPlugin
    options:
      filters:
        - "!DEFAULT_NAME"
