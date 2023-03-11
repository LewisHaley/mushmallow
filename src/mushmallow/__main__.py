"""Mushmallow CLI."""

import argparse
import pathlib

from . import fix_marshmallow


def parse_args():
    """Parse command-line arguments.

    :returns: parsed command-line arguments:
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=pathlib.Path,
        help="The file containing Marshmallow schemas to format and/or fix",
    )
    return parser.parse_args()


def main():
    """Mushmallow CLI entry-point."""
    args = parse_args()
    fix_marshmallow(args.file)


if __name__ == "__main__":
    main()
