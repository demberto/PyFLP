import argparse

from .flpinfo import FLPInfo

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="flpinfo", description=__doc__)
    arg_parser.add_argument(
        "flp_or_zip", help="The location of FLP/zipped FLP to show information about."
    )
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display verbose logging output and full lists",
    )
    arg_parser.add_argument(
        "--full-lists", action="store_true", help="Lists will not appear truncated."
    )
    arg_parser.add_argument(
        "--no-color", action="store_true", help="Disables colored output"
    )
    args = arg_parser.parse_args()
    FLPInfo(args).info()
