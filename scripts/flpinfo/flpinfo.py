"""Prints basic information about an FLP."""

import os

import colorama  # type: ignore

from pyflp import Parser


class FLPInfo:
    def __init__(self, args) -> None:
        colorama.init(autoreset=True)
        self.__bad_flp = False
        self.__term_cols = os.get_terminal_size().columns
        self.path = args.flp_or_zip
        self.__no_color = args.no_color
        self.__verbose = True if args.verbose else False
        self.__full_lists = args.full_lists

    def color(self, color, what):
        if self.__no_color:
            return what
        return color + str(what) + colorama.Style.RESET_ALL

    def green(self, what):
        return self.color(colorama.Fore.GREEN, what)

    def cyan(self, what):
        return self.color(colorama.Fore.CYAN, what)

    def yellow(self, what):
        return self.color(colorama.Fore.YELLOW, what)

    def blue(self, what):
        return self.color(colorama.Fore.BLUE, what)

    def bright(self, what):
        return self.color(colorama.Style.BRIGHT, what)

    def red(self, what):
        self.__bad_flp = True
        return self.color(colorama.Fore.RED, what)

    def print_col(self, kind, what):
        """Clip output to the end of a terminal columns.
        This will ensure long lists get truncated."""
        kind = self.bright(kind)
        if not (self.__verbose or self.__full_lists):
            if len(what) > self.__term_cols:
                end = "...]" if what[-1] == "]" else "..."
                what = what[: self.__term_cols - 20] + end
        print(kind, what)

    def info(self):
        project = Parser(self.__verbose).parse(self.path)

        # Separate logging and program output
        if self.__verbose:
            print("")

        misc = project.misc
        self.print_col("Title:           ", self.green(misc.title))
        self.print_col("Artist(s):       ", self.green(misc.artists))
        self.print_col("Genre:           ", self.green(misc.genre))
        # !self.print_col("Comments:        ", self.green(misc.comment))

        url = self.cyan(misc.url) if misc.url else ""
        self.print_col("Project URL:     ", url)
        self.print_col("FL Version:      ", self.green(misc.version))

        ch_len = len(project.channels)
        if ch_len == 0:
            channels = self.red(0)
        else:
            _names = []
            for ch in project.channels:
                if ch.name:
                    name = ch.name
                else:
                    name = ch.default_name
                _names.append(self.blue(name))
            channels = f"{self.green(ch_len)} [{', '.join(_names)}]"
        self.print_col("Channel(s):      ", channels)

        arr_len = len(project.arrangements)
        if arr_len == 0:
            arrangements = self.red(0)
        else:
            _names = [self.blue(arr.name) for arr in project.arrangements]
            arrangements = f"{self.green(arr_len)} [{', '.join(_names)}]"
        self.print_col("Arrangement(s):  ", arrangements)

        pat_len = len(project.patterns)
        if pat_len == 0:
            patterns = self.yellow(0)
        else:
            _names = [self.blue(pattern.name) for pattern in project.patterns]
            patterns = f"{self.green(pat_len)} [{', '.join(_names)}]"
        self.print_col("Pattern(s):      ", patterns)

        note_count = 0
        for pattern in project.patterns:
            note_count += len(pattern.notes)
        notes = self.green(note_count) if note_count else self.yellow(0)
        self.print_col("Note(s):         ", notes)

        if self.__bad_flp:
            flp_inspect = self.cyan("FLPInspect")
            print(
                "\nFLP seems to have been corrupted,"
                f" try inspecting in {flp_inspect}"
            )
