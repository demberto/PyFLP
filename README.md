# PyFLP

PyFLP is an unofficial parser for [FL Studio](https://www.image-line.com/fl-studio/)
project and preset files written in Python.

<!-- SHIELDS -->
<!-- markdownlint-disable -->
<table>
  <colgroup>
    <col style="width: 10%;"/>
    <col style="width: 90%;"/>
  </colgroup>
  <tbody>
    <tr>
      <th>CI</th>
      <td>
        <img alt="build" src="https://github.com/demberto/PyFLP/actions/workflows/publish.yml/badge.svg"/>
        <a href="https://pyflp.readthedocs.io/en/latest/">
          <img alt="Documentation Build Status" src="https://img.shields.io/readthedocs/pyflp/latest?logo=read-the-docs"/>
        </a>
        <a href="https://results.pre-commit.ci/latest/github/demberto/PyFLP/master">
          <img alt="pre-commit-ci" src="https://results.pre-commit.ci/badge/github/demberto/PyFLP/master.svg"/>
        </a>
      </td>
    </tr>
    <tr>
      <th>PyPI</th>
      <td>
        <a href="https://pypi.org/project/PyFLP">
          <img alt="PyPI - Package Version" src="https://img.shields.io/pypi/v/PyFLP"/>
        </a>
        <a href="https://pypi.org/project/PyFLP">
          <img alt="PyPI - Supported Python Versions" src="https://img.shields.io/pypi/pyversions/PyFLP?logo=python&amp;logoColor=white"/>
        </a>
        <a href="https://pypi.org/project/PyFLP">
          <img alt="PyPI - Supported Implementations" src="https://img.shields.io/pypi/implementation/PyFLP"/>
        </a>
        <a href="https://pypi.org/project/PyFLP">
          <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/PyFLP"/>
        </a>
      </td>
    </tr>
    <tr>
      <th>Activity</th>
      <td>
        <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2023"/>
        <a href="https://pypistats.org/packages/pyflp">
          <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/PyFLP"/>
        </a>
      </td>
    </tr>
    <tr>
      <th>QA</th>
      <td>
        <a href="https://codecov.io/gh/demberto/PyFLP">
          <img alt="codecov" src="https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF"/>
        </a>
        <a href="https://codefactor.io/repository/github/demberto/PyFLP">
          <img alt="CodeFactor Grade" src="https://img.shields.io/codefactor/grade/github/demberto/PyFLP?logo=codefactor"/>
        </a>
        <a href="http://mypy-lang.org/">
          <img alt="Checked with mypy" src="http://www.mypy-lang.org/static/mypy_badge.svg">
        </a>
        <a href="https://github.com/pre-commit/pre-commit">
          <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&amp;logoColor=white"/>
        </a>
        <a href="https://github.com/PyCQA/bandit">
          <img alt="Security Status" src="https://img.shields.io/badge/security-bandit-yellow.svg"/>
        </a>
      </td>
    </tr>
    <tr>
      <th>Other</th>
      <td>
        <a href="https://github.com/demberto/PyFLP/blob/master/LICENSE">
          <img alt="License" src="https://img.shields.io/github/license/demberto/PyFLP"/>
        </a>
        <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/demberto/PyFLP"/>
        <a href="https://github.com/psf/black">
          <img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-black"/>
        </a>
        <a href="https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md">
          <img alt="covenant" src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg"/>
        </a>
      </td>
    </tr>
  </tbody>
</table>
<!-- markdownlint-restore -->

From a very general point-of-view, this is the state of what is currently
implemented. Click on a link to go to the documentation for that feature.

<!-- FEATURE TABLE -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <th>Group</th>
    <th>Feature</th>
    <th>Issues</th>
  </tr>
  <tr>
    <td rowspan="3">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/arrangements.html">Arrangements</a><br/>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aarrangement-general">
        <img alt="open arrangement-general issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/arrangement-general?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aarrangement-general">
        <img alt="closed arrangement-general issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/arrangement-general?label=closed&style=flat-square"/>
      </a>
    </td>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/arrangements.html#playlist">🎼 Playlist</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aarrangement-playlist">
        <img alt="open arrangement-playlist issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/arrangement-playlist?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aarrangement-playlist">
        <img alt="closed arrangement-playlist issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/arrangement-playlist?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr></tr> <!-- only for formatting --->
  <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/arrangements.html#track">🎞️ Tracks</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aarrangement-track">
        <img alt="open arrangement-track issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/arrangement-track?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aarrangement-track">
        <img alt="closed arrangement-track issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/arrangement-track?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td rowspan="4">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/channels.html">Channel Rack</a><br/>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Achannel-general">
        <img alt="open channel-general issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/channel-general?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Achannel-general">
        <img alt="closed channel-general issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/channel-general?label=closed&style=flat-square"/>
      </a>
    </td>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/channels.html#pyflp.channel.Automation">📈 Automations</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%channel-automation">
        <img alt="open channel-automation issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/channel-automation?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Achannel-automation">
        <img alt="closed channel-automation issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/channel-automation?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/channels.html#pyflp.channel.Instrument">🎹 Instruments</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Achannel-instrument">
        <img alt="channel-instrument issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/channel-instrument?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Achannel-instrument">
        <img alt="closed channel-instrument issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/channel-instrument?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/channels.html#pyflp.channel.Layer">📚 Layer</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Achannel-layer">
        <img alt="open channel-layer issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/channel-layer?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Achannel-layer">
        <img alt="closed channel-layer issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/channel-layer?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/channels.html#pyflp.channel.Sampler">📁 Sampler</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Achannel-sampler">
        <img alt="open channel-sampler issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/channel-sampler?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Achannel-sampler">
        <img alt="closed channel-sampler issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/channel-sampler?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td rowspan="2">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/mixer.html">Mixer</a><br/>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Amixer-general">
        <img alt="open mixer-general issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/mixer-general?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Amixer-general">
        <img alt="closed mixer-general issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/mixer-general?label=closed&style=flat-square"/>
      </a>
    </td>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/mixer.html#pyflp.mixer.Insert">🎚️ Inserts</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Amixer-insert">
        <img alt="open mixer-insert issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/mixer-insert?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Amixer-insert">
        <img alt="closed mixer-insert issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/mixer-insert?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
    <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/mixer.html#pyflp.mixer.Slot">🎰 Effect slots</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Amixer-slot">
        <img alt="open mixer-slot issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/mixer-slot?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Amixer-slot">
        <img alt="closed mixer-slot issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/mixer-slot?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td rowspan="3">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/patterns.html">🎶 Patterns</a><br/>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Apattern-general">
        <img alt="open pattern-general issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/pattern-general?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Apattern-general">
        <img alt="closed pattern-general issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/pattern-general?label=closed&style=flat-square"/>
      </a>
    </td>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/patterns.html#pyflp.pattern.Controller">🎛 Controllers</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Apattern-controller">
        <img alt="open pattern-controller issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/pattern-controller?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Apattern-controller">
        <img alt="closed pattern-controller issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/pattern-controller?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
    <tr>
    <td><a href="https://pyflp.readthedocs.io/en/latest/reference/patterns.html#pyflp.pattern.Note">🎵 Notes</a></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Apattern-note">
        <img alt="open pattern-note issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/pattern-note?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Apattern-note">
        <img alt="closed pattern-note issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/pattern-note?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr></tr> <!-- for formatting --->
  <tr>
    <td>
      <a href="https://pyflp.readthedocs.io/en/latest/reference/timemarkers.html">🚩 Timemarkers</a>
    </td>
    <td></td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Atimemarker">
        <img alt="open timemarker issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/timemarker?label=open&style=flat-square"/>
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Atimemarker">
        <img alt="closed timemarker issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/timemarker?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td rowspan="2">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/plugins.html">Plugins</a>
    </td>
    <td>
      Native -
      8 <a href="https://pyflp.readthedocs.io/en/latest/reference/plugins.html#effects">effects</a>,
      1 <a href="https://pyflp.readthedocs.io/en/latest/reference/plugins.html#generators">synth</a>
    </td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aplugin-native">
        <img alt="open plugin-native issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/plugin-native?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aplugin-native">
        <img alt="closed plugin-native issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/plugin-native?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://pyflp.readthedocs.io/en/latest/reference/plugins.html#pyflp.plugin.VSTPlugin">VST 2/3</a>
    </td>
    <td>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aplugin-3rdparty">
        <img alt="plugin-3rdparty issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/plugin-3rdparty?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aplugin-3rdparty">
        <img alt="closed plugin-3rdparty issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/plugin-3rdparty?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
  <tr>
    <td rowspan="2" colspan="2">
      <a href="https://pyflp.readthedocs.io/en/latest/reference/project.html">Project</a>
      - Settings and song metadata
    </td>
    <td colspan="2">
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aopen+is%3Aissue+label%3Aproject-general">
        <img alt="open project-general issues" src="https://img.shields.io/github/issues-raw/demberto/PyFLP/project-general?label=open&style=flat-square">
      </a>
      <a href="https://github.com/demberto/PyFLP/issues?q=is%3Aclosed+is%3Aissue+label%3Aproject-general">
        <img alt="closed project-general issues" src="https://img.shields.io/github/issues-closed-raw/demberto/PyFLP/project-general?label=closed&style=flat-square"/>
      </a>
    </td>
  </tr>
</table>
<!-- markdownlint-restore -->

## ⏬ Installation

CPython 3.7+ / PyPy 3.8+ required.

```none
python -m pip install -U pyflp
```

## ▶ Usage

[Load](https://pyflp.readthedocs.io/en/latest/reference.html#pyflp.parse) a project file:

```py
import pyflp
project = pyflp.parse("/path/to/parse.flp")
```

> If you get any sort of errors or warnings while doing this, please open an
> [issue](https://github.com/demberto/PyFLP/issues).

[Save](https://pyflp.readthedocs.io/en/latest/reference.html#pyflp.save) the project:

```py
pyflp.save(project, "/path/to/save.flp")
```

> It is advised to do a backup of your projects before doing any changes.
> It is also recommended to open the modified project in FL Studio to ensure
> that it works as intended.

Check the [reference](https://pyflp.rtfd.io/en/latest/reference.html) for a
complete list of useable features.

## 🙏 Acknowledgements

- Monad.FLParser: <https://github.com/monadgroup/FLParser>
- FLPEdit (repo deleted by [author](https://github.com/roadcrewworker))

## ✨ Contributors

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful people:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/nickberry17"><img src="https://avatars.githubusercontent.com/u/18670565?v=4?s=50" width="50px;" alt=""/><br /><sub><b>nickberry17</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/commits?author=nickberry17" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/zacanger"><img src="https://avatars.githubusercontent.com/u/12520493?v=4?s=50" width="50px;" alt=""/><br /><sub><b>zacanger</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/issues?q=author%3Azacanger" title="Bug reports">🐛</a> <a href="https://github.com/demberto/PyFLP/commits?author=zacanger" title="Documentation">📖</a></td>
      <td align="center"><a href="https://github.com/ttaschke"><img src="https://avatars.githubusercontent.com/u/7067750?v=4?s=50" width="50px;" alt=""/><br /><sub><b>Tim</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/commits?author=ttaschke" title="Documentation">📖</a> <a href="https://github.com/demberto/PyFLP/commits?author=ttaschke" title="Code">💻</a> <a href="#maintenance-ttaschke" title="Maintenance">🚧</a></td>
    </tr>
  </tbody>
</table>
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://allcontributors.org/) specification.
Contributions of any kind are welcome!

Please see the [contributor's guide](https://pyflp.rtfd.io/en/latest/contributing.html)
for more information about contributing.

## 📧 Contact

You can contact me either via [issues](https://github.com/demberto/PyFLP/issues)
and [discussions](https://github.com/demberto/PyFLP/discussions) or through
email via ``demberto(at)proton(dot)me``.

## © License

The code in this project has been licensed under the
[GNU Public License v3](https://www.gnu.org/licenses/gpl-3.0.en.html).
