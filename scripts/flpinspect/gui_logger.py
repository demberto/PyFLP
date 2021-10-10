# type: ignore

"""
https://stackoverflow.com/a/18194597
https://stackoverflow.com/a/37188648
"""

import logging
from tkinter.scrolledtext import ScrolledText


class GUIHandler(logging.Handler):
    """Used to redirect logging output to a `tk.ScrolledText` widget."""

    def __init__(self, console: ScrolledText):
        logging.Handler.__init__(self)
        self.console = console
        self.console.tag_config("INFO", foreground="black")
        self.console.tag_config("DEBUG", foreground="grey")
        self.console.tag_config("WARNING", foreground="orange")
        self.console.tag_config("ERROR", foreground="red")
        self.console.tag_config("CRITICAL", foreground="red", underline=1)

    def format(self, record: logging.LogRecord):
        r = record
        return f"[{r.levelname}] {r.name} <{r.module}.{r.funcName}>  {r.message}"

    def emit(self, record: logging.LogRecord):
        formattedMessage = self.format(record) + "\n"
        self.console.configure(state="normal")  # Enable writing
        self.console.insert(
            "end", formattedMessage, record.levelname
        )  # Write from the end
        self.console.configure(state="disabled")  # Disable writing
        self.console.see("end")  # Move cursor to the end
        self.console.update()
