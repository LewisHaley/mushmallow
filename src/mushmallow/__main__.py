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
    parser.add_argument(
        "--max-line-length",
        default=80,
        type=int,
        help="How many characters per line to allow",
    )
    parser.add_argument(
        "--indent-size",
        default=4,
        type=int,
        help="The number of spaces per indent",
    )
    parser.add_argument(
        "--fix-kwargs-for-marshmallow-4",
        action="store_true",
        help="If True, convert kwarg fields to metadata fields as per Marshmallow 4",
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        help=(
            "Sort kwarg and/or metadata fields alphabetically. Otherwise "
            "ordering is arbitrary."
        ),
    )
    return parser.parse_args()


def main():
    """Mushmallow CLI entry-point."""
    args = parse_args()
    fix_marshmallow(
        args.file,
        max_line_length=args.max_line_length,
        indent_size=args.indent_size,
        fix_kwargs_for_marshmallow_4=args.fix_kwargs_for_marshmallow_4,
        sort=args.sort,
    )


if __name__ == "__main__":
    main()
