# PyFLP

PyFLP is a parser for FL Studio project files written in Python.

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
        <img alt="build" src="https://img.shields.io/github/workflow/status/demberto/pyflp/main"/>
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
        <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2022"/>
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

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

## ⏬ Installation

**Python 3.7+** required:

```console
python -m pip install -U pyflp
```

[Alternate ways to install](https://pyflp.rtfd.io/).

## ▶ Usage

Load a project file:

```py
import pyflp
project = pyflp.parse("/path/to/parse.flp")
```

Save the project:

```py
pyflp.save(project, "/path/to/save.flp")
```

Check the [user guide](https://pyflp.rtfd.io/en/latest/user-guide)

## 🙏 Acknowledgements

- Monad.FLParser: <https://github.com/monadgroup/FLParser>
- FLPEdit (repo deleted by [author](https://github.com/roadcrewworker))

## ✨ Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/nickberry17"><img src="https://avatars.githubusercontent.com/u/18670565?v=4?s=50" width="50px;" alt=""/><br /><sub><b>nickberry17</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/commits?author=nickberry17" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/zacanger"><img src="https://avatars.githubusercontent.com/u/12520493?v=4?s=50" width="50px;" alt=""/><br /><sub><b>zacanger</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/issues?q=author%3Azacanger" title="Bug reports">🐛</a> <a href="https://github.com/demberto/PyFLP/commits?author=zacanger" title="Documentation">📖</a></td>
      <td align="center"><a href="https://github.com/ttaschke"><img src="https://avatars.githubusercontent.com/u/7067750?v=4?s=50" width="50px;" alt=""/><br /><sub><b>Tim</b></sub></a><br /><a href="https://github.com/demberto/PyFLP/commits?author=ttaschke" title="Documentation">📖</a> <a href="https://github.com/demberto/PyFLP/commits?author=ttaschke" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors] specification. Contributions of
any kind are welcome!

Please see the [contributor's guide][contributors-guide] for more information
about contributing.

## © License

The code in this project has been licensed under the [GNU Public License v3][gpl3].

<!-- LINKS -->
[contributors-guide]: https://github.com/demberto/PyFLP/blob/master/CONTRIBUTING.md
[gpl3]: https://www.gnu.org/licenses/gpl-3.0.en.html
