"""FLP event viewer, made using Ttk's Treeview.

Treeview tooltips:  https://stackoverflow.com/a/68243086
Treeview reset:     https://stackoverflow.com/a/66967466
"""

import pathlib
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfiledlg
import tkinter.messagebox as tkmsgbox
from tkinter.scrolledtext import ScrolledText

from pyflp import Parser
from pyflp.event import ByteEvent, WordEvent, DWordEvent, TextEvent
from pyflp.flobject.insert.event import InsertParamsEvent

from .gui_logger import GUIHandler  # type: ignore
from .treeview import Treeview


class FLPInspector(tk.Tk):
    def __init__(self, flp: str = "", verbose: bool = True):

        # Init
        super().__init__()
        self.title("FLPInspect")
        self.geometry("600x600")
        self.option_add("*tearOff", tk.FALSE)
        self.style = ttk.Style()

        # Top Menubar
        menubar = tk.Menu()
        self["menu"] = menubar

        # Menubar -> File
        menu_file = tk.Menu(menubar)
        menu_file.add_command(
            label="Open", command=self.file_open, accelerator="Ctrl+O", underline=1
        )
        self.bind("<Control-o>", self.file_open)
        menubar.add_cascade(menu=menu_file, label="File")

        # Menubar -> Preferences
        menu_prefs = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_prefs, label="Preferences")

        # Menubar -> Preferences -> Theme
        prefs_theme = tk.Menu(menu_prefs)
        menu_prefs.add_cascade(menu=prefs_theme, label="Theme")
        themes = self.style.theme_names()
        self.theme = tk.StringVar()
        for t in themes:
            prefs_theme.add_radiobutton(
                label=t, value=t, variable=self.theme, command=self.change_theme
            )

        # Menubar -> View
        menu_view = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_view, label="View")

        # All radiobuttons of prefs_theme are bound to self.theme.
        # Select the radiobutton has the name of currently used theme.
        # Without this, no radiobutton will be selected by default.
        self.theme.set(self.style.theme_use())

        # Menubar -> Help
        menu_help = tk.Menu(menubar)
        menu_help.add_command(label="About", command=self.show_about)
        menubar.add_cascade(menu=menu_help, label="Help")

        # Status bar at the bottom
        self.sb = tk.Label(bd=1, relief="sunken", anchor="s", height="1")
        self.sb.pack(side="bottom", fill="x")

        # PanedWindow to split area between Treeview and ScrolledText
        self.pw = tk.PanedWindow(bd=4, sashwidth=10, orient="vertical")
        self.pw.pack(fill="both", expand=tk.TRUE)

        # Treeview
        self.nb = ttk.Notebook(self.pw)
        self.tv = Treeview(self.nb, columns=("#1", "#2", "#3"), show="tree headings")
        self.tv.pack(side="left", expand=tk.TRUE, fill="both")
        self.nb.add(self.tv, text="Event View")
        self.nb.pack(fill="both", expand=tk.TRUE)
        self.pw.add(self.nb, height=400)

        # Menubar -> View -> Tooltips
        self.__show_htips = tk.BooleanVar(value=True)
        menu_view.add_checkbutton(
            label="Tooltips", variable=self.__show_htips, command=self.tv.toggle_htips
        )

        # Columns
        self.tv.column("#0", minwidth=20, width=20, stretch=False)
        self.tv.column("#1", width=60, anchor="w", stretch=False)
        self.tv.heading("#1", text="Index", sort_by="index")
        self.tv.column("#2", width=150, anchor="w", stretch=False)
        self.tv.heading("#2", text="Event", sort_by="event")
        self.tv.column("#3", width=200, anchor="w")
        self.tv.heading("#3", text="Value")

        # Menubar -> Preferences -> Editable
        self.__editable = tk.BooleanVar(value=True)
        menu_prefs.add_checkbutton(
            label="Editable", variable=self.__editable, command=self.tv.toggle_editing
        )

        # ScrolledText to display Parser logs
        self.console = ScrolledText(self.pw, bg="#D3D3D3")
        self.console.pack(side="bottom")
        self.pw.add(self.console, height=100)

        # Menubar -> View -> Console
        self.__console_visible = tk.BooleanVar(value=True)
        menu_view.add_checkbutton(
            label="Console",
            variable=self.__console_visible,
            command=self.toggle_console,
        )

        # Window doesn't appear without this unless FLP gets parsed without this
        self.update_idletasks()

        # Verbosity
        self.verbose = verbose
        if not self.verbose:
            self.console.insert(
                "end",
                "Logging has been disabled. "
                "Run with -v option to see detailed log information",
            )

        # If called with args from command line
        if flp:
            self.populate_table(pathlib.Path(flp))

        self.mainloop()

    def change_theme(self):
        self.style.theme_use(self.theme.get())

    def update_status(self, event: tk.Event):
        if self.tv.identify_region(event.x, event.y) == "cell":
            row = self.tv.identify_row(event.y)
            index = self.tv.item(row, "values")[0]
            self.sb.config(text=repr(self.events[int(index)]))

    def toggle_console(self):

        # Doesn't work properly without the 'not'
        if not self.__console_visible.get():
            self.pw.forget(self.console)
        else:
            self.pw.add(self.console)

    def populate_table(self, file: pathlib.Path):
        gui_handler = GUIHandler(self.console)
        parser = Parser(verbose=self.verbose, handlers=[gui_handler])
        project = None
        if file.suffix == ".zip":
            # TODO Parser.get_events for ZIPs
            project = parser.parse_zip(file)
        else:
            try:
                project = parser.parse(file)
            except Exception as e:
                # Failsafe mode
                self.console.config(state="normal")
                self.console.insert(
                    "end",
                    "Failed to parse properly; only events will be shown. "
                    f"\nException details: {e}",
                    "ERROR",
                )
                self.console.config(state="disabled")
                self.events = parser.get_events(file)
            else:
                self.events = project.events

        for ev in self.events:
            if isinstance(ev, ByteEvent):
                value = ev.to_int8()
                if value < 0:
                    i8 = value
                    u8 = ev.to_uint8()
                    value = f"{i8} / {u8}"  # type: ignore
            elif isinstance(ev, WordEvent):
                value = ev.to_int16()
                if value < 0:
                    i16 = value
                    u16 = ev.to_uint16()
                    value = f"{i16} / {u16}"  # type: ignore
            elif isinstance(ev, DWordEvent):
                value = ev.to_int32()
                if value < 0:
                    i32 = value
                    u32 = ev.to_uint32()
                    value = f"{i32} / {u32}"  # type: ignore
            elif isinstance(ev, TextEvent):
                value = ev.to_str()  # type: ignore
            else:
                if ev.id == InsertParamsEvent.ID:
                    value = (
                        "--- Displaying/editing this value "  # type: ignore
                        "causes a crash, hence it is disabled ---"
                    )
                else:
                    value = str(tuple(ev.data))  # type: ignore
            self.tv.insert("", "end", values=(ev.index, ev.id, value))
        self.sb.config(text="Ready")

    def file_open(self, _=None):
        """Command for File -> Open and callback for Ctrl+O accelerator.

        Args:
            _ (tk.Event): Not required by this function, kept for bind()
        """

        file = tkfiledlg.askopenfilename(
            title="Select an FLP or a ZIP looped package",
            filetypes=(("FL Studio project", "*.flp"), ("ZIP looped package", "*.zip")),
        )

        if file:
            for i in self.tv.get_children():
                self.tv.delete(i)
            # self.update()
            self.console.delete("0.0", "end")
            self.populate_table(pathlib.Path(file))
            self.bind("<Motion>", self.update_status)

    def show_about(self):
        tkmsgbox.showinfo("About", "FLPInspect - Inspect your FLPs")
