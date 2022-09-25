|vscode-icon| VSCode integration
================================

I use VSCode for development. I have made certain changes to the workspace to
suit my workflows and make life easier.

.. todo Inspect whether venv creation can be automated through VSCode.

Python extension configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To ease linting, enforce strict type checking and improve code quality, I have
modified certain settings for the official Python / Pylance extension, so that
you don't need to manually configure it or encounter issues while committing.
Check `settings.json
<https://github.com/demberto/PyFLP/blob/master/.vscode/settings.json>`_.

Recommended extensions
^^^^^^^^^^^^^^^^^^^^^^

When you open the repo directory in VSCode, you will get recommendations for
extensions. I use these extensions myself. You can check `extensions.json
<https://github.com/demberto/PyFLP/blob/master/.vscode/extensions.json>`_ to
know why and where they are used.

Tasks
^^^^^

If you use Windows, I have made some shortcuts for common tasks. Check
`tasks.json <https://github.com/demberto/PyFLP/blob/master/.vscode/tasks.json>`_.

.. |vscode-icon| image:: /img/contributing/vscode.svg
   :width: 32
