import argparse

from .inspector import FLPInspector

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="flpinspect", description=__doc__)
    arg_parser.add_argument("--flp", help="The FLP to open in event viewer.")
    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display verbose logs. Takes significantly more time to parse",
    )
    args = arg_parser.parse_args()
    FLPInspector(args.flp, args.verbose)
