"""Mushmallow CLI."""

import argparse
import difflib
import pathlib

from .core import format_marshmallow


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
    parser.add_argument(
        "--diff",
        action="store_true",
        help=(
            "Don't write the alterations to the target file, instead produce a diff "
            "between."
        ),
    )
    return parser.parse_args()


def colourize_diff(line):
    """Colourize a line of unified diff.

    :param str line: the line of diff to colourize

    :returns: the colourized line
    :rtype: str
    """
    no_color = "\033[0m"
    red = "\033[0;31m"
    green = "\033[0;32m"
    if line.startswith("-"):
        line = f"{red}{line}{no_color}"
    elif line.startswith("+"):
        line = f"{green}{line}{no_color}"

    return line


def print_diff(orig_lines, new_lines):
    """Print the unified diff between two sets of lines.

    The diff is written to stdout.

    :param list[str] orig_lines: the original lines from the user's file
    :param list[str] new_lines: the modified lines
    """
    diff = difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile="before",
        tofile="after",
    )
    print("\n".join(map(colourize_diff, diff)), end="")


def main():
    """Mushmallow CLI entry-point."""
    args = parse_args()

    orig_lines = args.file.read_text().splitlines()
    new_lines = format_marshmallow(
        orig_lines,
        max_line_length=args.max_line_length,
        indent_size=args.indent_size,
        fix_kwargs_for_marshmallow_4=args.fix_kwargs_for_marshmallow_4,
        sort=args.sort,
    )

    if args.diff:
        print_diff(orig_lines, new_lines)
    else:
        new_text = "\n".join(new_lines)
        if orig_lines:
            new_text += "\n"
        args.file.write_text(new_text)


if __name__ == "__main__":
    main()
