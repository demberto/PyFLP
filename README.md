<!-- PROJECT SHIELDS -->
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![GitHub Workflow Status][workflow-shield]][workflow-shield]
[![Documentation Status][docs-shield]][docs-link]
[![codecov][codecov-badge]][codecov-link]
[![CodeFactor][codefactor-badge]][codefactor-link]
[![PyPI - License][license-shield]][license-link]
[![PyPI - Version][version-shield]][version-shield]
[![PyPI - Python Version][pyversions-shield]][pyversions-shield]
[![Contributor Covenant][covenant-shield]][covenant-link]
[![Code Style: Black][black-shield]][black-link]

# PyFLP

PyFLP is a parser for FL Studio project (.flp) files written in Python.

## ⏬ Installation

PyFLP requires Python 3.6+

```
pip install --upgrade pyflp
```

[Alternate ways to install](https://pyflp.rtfd.io/en/latest/installation).

## ▶ Usage

To load a project:

```py
import pyflp
project = pyflp.parse("/path/to/parse.flp")
```

To save the project:

```py
pyflp.save(project, "/path/to/save.flp")
```

## 🙏 Acknowledgements

Monad.FLParser: https://github.com/monadgroup/FLParser

FLPEdit (repo deleted by [author](https://github.com/roadcrewworker))

## 🤝 Contributing

Please see the [contributor's guide][contributors-guide].

## ✨ Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/nickberry17"><img src="https://avatars.githubusercontent.com/u/18670565?v=4?s=100" width="100px;" alt=""/><br /><sub><b>nickberry17</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/commits?author=nickberry17" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors] specification. Contributions of
any kind are welcome!

## © License

The code in this project has been licensed under the [GNU Public License v3][gpl3-link].

<!-- BADGES / SHIELDS -->
[black-shield]: https://img.shields.io/badge/code%20style-black-black
[codecov-badge]: https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF
[codefactor-badge]: https://www.codefactor.io/repository/github/demberto/pyflp/badge
[covenant-shield]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
[docs-shield]: https://readthedocs.org/projects/pyflp/badge/?version=latest
[license-shield]: https://img.shields.io/pypi/l/pyflp
[pyversions-shield]: https://img.shields.io/pypi/pyversions/pyflp
[version-shield]: https://img.shields.io/pypi/v/pyflp
[workflow-shield]: https://img.shields.io/github/workflow/status/demberto/pyflp/main

<!-- LINKS -->
[all-contributors]: https://github.com/all-contributors/all-contributors
[black-link]: https://github.com/psf/black
[codecov-link]: https://codecov.io/gh/demberto/PyFLP
[codefactor-link]: https://www.codefactor.io/repository/github/demberto/pyflp
[contributors-guide]: https://github.com/demberto/PyFLP/blob/master/CONTRIBUTING.md
[covenant-link]: https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md
[docs-link]: https://pyflp.readthedocs.io/en/latest/
[gpl3-link]: https://www.gnu.org/licenses/gpl-3.0.en.html
[license-link]: https://github.com/demberto/PyFLP/blob/master/LICENSE
