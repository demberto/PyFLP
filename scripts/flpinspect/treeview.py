"""
Treeview implementation used by FLPInspect

Stackoverflow to my rescue :)

Sorting:                        https://stackoverflow.com/a/63432251
Editable cells:                 https://stackoverflow.com/a/18815802
Column resize event:            https://stackoverflow.com/a/47697226
Entry scrolling (mousewheel):   https://stackoverflow.com/a/61977144
Entry scrolling (scrollbar):    https://stackoverflow.com/a/61977043

Godmode treeview:   https://github.com/unodan/TkInter-Treeview-Example-Demo
"""

import tkinter as tk
from tkinter import TclError, ttk
from functools import partial


class EntryPopup(ttk.Entry):
    def __init__(self, tv: ttk.Treeview, iid, text, **kw):
        """If relwidth is set, then width is ignored"""
        super().__init__(tv, **kw)
        self.tv = tv
        self.iid = iid

        self.insert(0, text)
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self["exportselection"] = False

        self.focus_force()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda _: self.destroy())
        self.bind("<MouseWheel>", lambda _: self.destroy())

    def on_return(self, event: tk.Event):
        values = list(self.tv.item(self.iid, "values"))
        values[-1] = self.get()
        self.tv.item(self.iid, values=values)
        self.destroy()

    def select_all(self, _):
        """Set selection on the whole text."""
        self.selection_range(0, "end")

        # returns 'break' to interrupt default key-bindings
        return "break"


class Treeview(ttk.Treeview):
    """A Treeview which supports cell-editing, \
    row-sorting and handles column resizing.

    NOTE: It is assumed that column headings are #0, #1, #2... and so on.
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<B1-Motion>", self.on_resize)
        self.bind("<Motion>", self.show_htip)
        self.bind("<MouseWheel>", self.close_popup)
        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.vsb.bind("<B1-Button>", self.close_popup)
        self.vsb.pack(side="right", fill="y")
        self.hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.hsb.bind("<B1-Button>", self.close_popup)
        self.hsb.pack(side="bottom", fill="x")
        self.configure(xscrollcommand=self.hsb.set, yscrollcommand=self.vsb.set)
        self.htip = ttk.Label(
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font="TkFixedFont",
            wraplength=300,
        )
        self.__hid = ""
        self.show_htips = self.editable = True

    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, "command"):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs["command"] = partial(func, column, False)
            else:
                raise TclError(f"No such sort algorithm '{sort_by}'")
        return super().heading(column, **kwargs)

    def __sort(self, column, reverse, data_type, callback):
        l = [(self.set(k, column), k) for k in self.get_children("")]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.move(k, "", index)
        self.heading(column, command=partial(callback, column, not reverse))

    def _sort_by_index(self, column, reverse):
        self.__sort(column, reverse, int, self._sort_by_index)

    def _sort_by_event(self, column, reverse):
        self.__sort(column, reverse, str, self._sort_by_event)

    def close_popup(self, _: tk.Event = None):
        """Close entry popup"""
        if hasattr(self, "ep"):
            self.ep.destroy()

    def toggle_htips(self):
        self.htip.place_forget()
        self.show_htips = not self.show_htips

    def on_resize(self, e: tk.Event):
        """Detect column resizing, resize `self.ep` if active."""

        if not self.identify_region(e.x, e.y) == "separator":
            return

        if hasattr(self, "ep"):
            col0_w = self.column("#0", "width")
            col1_w = self.column("#1", "width")
            col2_w = self.column("#2", "width")
            col3_w = self.column("#3", "width")
            self.ep.place_configure(x=col0_w + col1_w + col2_w, width=col3_w)

    def toggle_editing(self):
        self.editable = not self.editable
        self.close_popup()

    def place_htip(self, text: str, x: int, y: int):
        if self.__hid:
            # self.htip.place_forget()
            self.after_cancel(self.__hid)
        self.__hid = self.after(1000, self.htip.place, {"x": x + 20, "y": y - 20})
        self.htip.configure(text=text)

    def show_htip(self, event: tk.Event):
        if self.show_htips and self.identify_region(event.x, event.y) == "cell":
            self.htip.place_forget()
            row = self.identify_row(event.y)
            values = self.item(row, "values")
            if values:
                text = values[2]
                if len(text) >= 30:
                    self.place_htip(text, event.x, event.y)

    def on_double_click(self, event: tk.Event):
        """Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text"""

        # Close previous popups
        self.close_popup()

        # what row and column was clicked on
        row = self.identify_row(event.y)
        column = self.identify_column(event.x)

        # Show popup only when a cell in "Values" is clicked
        if column == "#3" and self.identify_region(event.x, event.y) == "cell":
            # get column position info
            x, y, width, height = self.bbox(row, column)

            # y-axis offset (This value will make the popup appear over
            # the cell, mimicking the behavior of an actual editable cell)
            pady = height // 2

            # place Entry popup properly
            text = self.item(row, "values")[2]
            state = "normal" if self.editable else "disabled"
            self.ep = EntryPopup(self, row, text, state=state)
            self.ep.place(x=x, y=y + pady, anchor="w", width=width)
