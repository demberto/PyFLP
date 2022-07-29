---
hide:
  - navigation
---

# Installation

## Via `pip` from PyPi **(RECOMMENDED)**:

```
pip install --upgrade pyflp
```

## Via `pip` from Github repo:

1.  Clone this repo

    ```
    git clone https://github.com/demberto/PyFLP
    ```

2.  Navigate to newly created folder

    ```
    cd PyFLP
    ```

3.  Install

    -   Normal installation:

        ```
        pip install .
        ```

        *This allows you to install a version with the latest changes from the
        repo. However, it might be broken.*

    *OR*

    -   Editable install:

        ```
        pip install -e .
        ```

        *Preferred way for developing and testing PyFLP, if virtualenv is not
        an option for you.*

## From Github releases:

1.  Go to [Releases](https://github.com/demberto/PyFLP/releases) tab.
2.  Download the build distrbution (**.whl**) wheel file and the source tarball,
    (**.tar.gz**) optionally.
3.  Install them via pip, for e.g.

    ```
    pip install pyflp-1.1.0-py3-none-any.whl
    ```
